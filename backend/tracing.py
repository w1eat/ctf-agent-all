"""Per-tool-call JSONL event tracing — one file per solver, streamable via tail -f."""

from __future__ import annotations

import asyncio
import atexit
import datetime as dt
import json
import logging
import re
import signal
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from pathlib import Path


def _sanitize(s: str) -> str:
    return s.replace("/", "_").replace(" ", "_")


def _safe_run_id(run_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", run_id or "adhoc")


_observed_signal: dict[str, object] | None = None


@contextmanager
def observe_exit_signals():
    """Record catchable terminal signals while preserving asyncio's handler."""
    global _observed_signal
    _observed_signal = None
    installed = []
    for name in ("SIGINT", "SIGBREAK"):
        signum = getattr(signal, name, None)
        if signum is None:
            continue
        try:
            previous = signal.getsignal(signum)
            if not callable(previous):
                continue

            def handler(number, frame, *, _previous=previous):
                global _observed_signal
                _observed_signal = {"signal": signal.Signals(number).name,
                                    "utc": dt.datetime.now(dt.UTC).isoformat()}
                _previous(number, frame)

            signal.signal(signum, handler)
            installed.append((signum, previous))
        except (OSError, ValueError):
            continue
    try:
        yield
    finally:
        for signum, previous in reversed(installed):
            signal.signal(signum, previous)
        _observed_signal = None


def cancellation_origin() -> dict[str, object]:
    return {"origin": "observed_signal", **_observed_signal} if _observed_signal else {
        "origin": "unknown_external_cancel"
    }


class _TeeStream:
    def __init__(self, original, output, lock: threading.RLock) -> None:
        self.original, self.output, self.lock = original, output, lock

    def write(self, data: str) -> int:
        with self.lock:
            result = self.original.write(data)
            try:
                self.output.write(data)
                self.output.flush()
            except Exception as exc:
                print(f"Run text log write failed: {exc}", file=self.original, flush=True)
            return result

    def flush(self) -> None:
        with self.lock:
            self.original.flush()
            try:
                self.output.flush()
            except Exception as exc:
                print(f"Run text log flush failed: {exc}", file=self.original, flush=True)

    def __getattr__(self, name: str):
        return getattr(self.original, name)


@contextmanager
def run_text_log(run_id: str, stamp: str, log_dir: str = "logs"):
    path = Path(log_dir) / f"run-{_safe_run_id(run_id)}-{stamp}.log"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        output = path.open("a", encoding="utf-8")
    except OSError as exc:
        print(f"Run text log open failed: {exc}", file=sys.stderr, flush=True)
        yield None
        return
    lock = threading.RLock()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    handler = logging.StreamHandler(output)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%X"))
    logging.getLogger().addHandler(handler)
    sys.stdout = _TeeStream(old_stdout, output, lock)
    sys.stderr = _TeeStream(old_stderr, output, lock)
    try:
        yield path
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        logging.getLogger().removeHandler(handler)
        try:
            handler.flush()
            handler.close()
            output.close()
        except Exception as exc:
            print(f"Run text log close failed: {exc}", file=old_stderr, flush=True)


def prune_run_logs(log_dir: str = "logs", *, keep_run: tuple[str, str] | None = None,
                   max_age_days: int = 7, max_bytes: int = 1 << 30) -> None:
    """Prune paired coordinator/text logs, never the active or newest run."""
    root = Path(log_dir)
    groups: dict[tuple[str, str], list[Path]] = {}
    pattern = re.compile(r"^(?:coordinator|run)-(.+)-(\d{8}-\d{6})\.(?:jsonl|log)$")
    for path in root.iterdir() if root.exists() else ():
        match = pattern.match(path.name)
        if match and path.is_file():
            groups.setdefault((match.group(1), match.group(2)), []).append(path)
    if not groups:
        return
    newest = max(groups, key=lambda key: key[1])
    protected = {newest}
    if keep_run:
        protected.add((_safe_run_id(keep_run[0]), keep_run[1]))
    cutoff = time.time() - max_age_days * 86400

    def remove_group(key):
        for path in groups.pop(key, []):
            try:
                path.unlink()
            except OSError as exc:
                print(f"Run log retention failed for {path}: {exc}", file=sys.stderr, flush=True)

    for key in sorted(groups, key=lambda item: item[1]):
        if key not in protected and max(p.stat().st_mtime for p in groups[key]) < cutoff:
            remove_group(key)
    total = sum(p.stat().st_size for paths in groups.values() for p in paths)
    for key in sorted(groups, key=lambda item: item[1]):
        if total <= max_bytes:
            break
        if key not in protected:
            size = sum(p.stat().st_size for p in groups[key])
            remove_group(key)
            total -= size


class SolverTracer:
    """Append-only JSONL event tracer. Flushes every write for tail -f streaming."""

    def __init__(self, challenge_name: str, model_id: str, log_dir: str = "logs") -> None:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        self.path = str(Path(log_dir) / f"trace-{_sanitize(challenge_name)}-{_sanitize(model_id)}-{ts}.jsonl")
        self._fh = open(self.path, "a")
        atexit.register(self._close)

    def close(self) -> None:
        """Explicitly close the trace file. Safe to call multiple times."""
        if not self._fh.closed:
            try:
                self._fh.close()
            except Exception:
                pass

    _close = close  # atexit compat

    def _write(self, event: dict) -> None:
        try:
            self._fh.write(json.dumps({"ts": time.time(), **event}) + "\n")
            self._fh.flush()
        except Exception:
            pass

    def tool_call(self, tool_name: str, args: dict | str, step: int) -> None:
        if tool_name.endswith("search_knowledge"):
            from backend.local_knowledge import normalized_keywords

            parameters = args if isinstance(args, dict) else {}
            keywords = normalized_keywords(str(parameters.get("query", "")))
            pending = getattr(self, "_pending_knowledge_queries", None)
            if pending is None:
                pending = self._pending_knowledge_queries = {}
            pending[step] = keywords
            self._write({"type": "knowledge_tool_call", "tool": tool_name,
                         "keywords": keywords, "step": step})
            return
        if tool_name.endswith("read_knowledge"):
            parameters = args if isinstance(args, dict) else {}
            self._write({"type": "knowledge_read_call", "tool": tool_name,
                         "document_id": str(parameters.get("document_id", ""))[:100], "step": step})
            return
        args_str = args if isinstance(args, str) else json.dumps(args)
        self._write({"type": "tool_call", "tool": tool_name, "args": args_str[:2000], "step": step})

    def tool_result(self, tool_name: str, result: str, step: int) -> None:
        if tool_name.endswith(("search_knowledge", "read_knowledge")):
            import ast

            data: object = result
            for _ in range(3):
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except (ValueError, TypeError):
                        try:
                            data = ast.literal_eval(data)
                        except (ValueError, SyntaxError):
                            break
                elif isinstance(data, dict) and isinstance(data.get("content"), list):
                    content = data["content"]
                    data = content[0].get("text", "") if content and isinstance(content[0], dict) else ""
                else:
                    break
            snapshots = getattr(self, "knowledge_snapshots", {})
            if tool_name.endswith("search_knowledge"):
                hits = data if isinstance(data, list) else []
                keywords = getattr(self, "_pending_knowledge_queries", {}).pop(step, "")
                self._write({"type": "knowledge_search", "tool": tool_name,
                             "keywords": keywords,
                             "external_snapshot": snapshots.get("external", ""),
                             "local_snapshot": snapshots.get("local", ""),
                             "hits": len(hits),
                             "document_ids": [str(hit.get("document_id", "")) for hit in hits
                                              if isinstance(hit, dict)][:10], "step": step})
            else:
                self._write({"type": "knowledge_read", "tool": tool_name,
                             "document_id": str(data.get("document_id", "")) if isinstance(data, dict) else "",
                             "snapshot_id": str(data.get("snapshot_id", "")) if isinstance(data, dict) else "",
                             "step": step})
            return
        self._write({"type": "tool_result", "tool": tool_name, "result": result[:2000], "step": step})

    def model_response(self, text: str, step: int, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self._write({"type": "model_response", "text": text[:1000], "step": step,
                      "input_tokens": input_tokens, "output_tokens": output_tokens})

    def usage(self, input_tokens: int, output_tokens: int, cache_read: int, cost_usd: float) -> None:
        self._write({"type": "usage", "input_tokens": input_tokens, "output_tokens": output_tokens,
                      "cache_read_tokens": cache_read, "cost_usd": round(cost_usd, 6)})

    def event(self, event_type: str, **kwargs) -> None:
        self._write({"type": event_type, **kwargs})


class CoordinatorTracer:
    """Append-only audit log for Coordinator turns, tools, and commands."""

    def __init__(self, run_id: str = "", log_dir: str = "logs", stamp: str = "") -> None:
        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self._warn_write_failure(exc)
        ts = stamp or time.strftime("%Y%m%d-%H%M%S")
        safe_run_id = _safe_run_id(run_id)
        self.path = str(Path(log_dir) / f"coordinator-{safe_run_id}-{ts}.jsonl")
        try:
            self._fh = open(self.path, "a", encoding="utf-8")
        except OSError as exc:
            self._fh = None
            self._warn_write_failure(exc)
        self.run_id = run_id or "adhoc"
        self.turn_id: str | None = None
        self._sequence = 0
        self._lock = threading.RLock()
        self._pending: dict[str, tuple[str, float]] = {}
        atexit.register(self._close)

    def close(self) -> None:
        with self._lock:
            if self._fh is None or self._fh.closed:
                return
            for call_id, (name, started) in list(self._pending.items()):
                self.event("operation_incomplete", call_id=call_id, operation=name,
                           duration_seconds=time.monotonic() - started)
            self._pending.clear()
            try:
                self._fh.close()
            except Exception as exc:
                self._warn_write_failure(exc)

    _close = close

    @staticmethod
    def _clip(value: object, limit: int = 20000) -> str:
        if isinstance(value, str):
            text = value
        else:
            try:
                text = json.dumps(value, ensure_ascii=False, default=str)
            except Exception:
                text = str(value)
        return text

    @staticmethod
    def _task_name() -> str | None:
        try:
            task = asyncio.current_task()
            return task.get_name() if task else None
        except RuntimeError:
            return None

    @staticmethod
    def _warn_write_failure(exc: BaseException) -> None:
        print(f"Coordinator trace write failed: {exc}", file=sys.stderr, flush=True)

    def _write(self, event: dict) -> None:
        with self._lock:
            if self._fh is None:
                return
            try:
                self._sequence += 1
                now = dt.datetime.now(dt.UTC)
                record = {"ts": now.timestamp(), "utc": now.isoformat(),
                          "run_id": self.run_id, "seq": self._sequence,
                          "task": self._task_name(), "turn_id": self.turn_id, **event}
                self._fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
                self._fh.flush()
            except Exception as exc:
                self._warn_write_failure(exc)

    def event(self, event_type: str, **kwargs) -> None:
        self._write({"type": event_type, **kwargs})

    def turn_input(self, text: str) -> None:
        self.turn_id = uuid.uuid4().hex
        self.event("turn_input", text=text)

    def tool_call(self, tool_name: str, args: object, call_id: str | None = None) -> str:
        call_id = self.start_operation("tool", tool_name, call_id=call_id)
        self.event("tool_call", call_id=call_id, tool=tool_name, args=self._clip(args))
        return call_id

    def tool_result(self, tool_name: str, result: object, call_id: str | None = None) -> None:
        self.event("tool_result", call_id=call_id, tool=tool_name, result=result)
        if call_id:
            self.end_operation(call_id, "completed")

    def start_operation(self, kind: str, name: str, input_value: object = None,
                        *, call_id: str | None = None, **fields: object) -> str:
        call_id = call_id or uuid.uuid4().hex
        with self._lock:
            self._pending[call_id] = (name, time.monotonic())
            self.event("operation_started", call_id=call_id, kind=kind,
                       operation=name, input=input_value, **fields)
        return call_id

    def end_operation(self, call_id: str, status: str, *, output: object = None,
                      error: BaseException | None = None, **fields: object) -> None:
        with self._lock:
            pending = self._pending.pop(call_id, None)
            self.event("operation_finished", call_id=call_id, status=status,
                       operation=pending[0] if pending else None,
                       duration_seconds=time.monotonic() - pending[1] if pending else None,
                       output=output,
                       error_type=type(error).__name__ if error else None,
                       error=str(error) if error else None,
                       traceback="".join(traceback.format_exception(error)) if error else None,
                       **fields)

    def pending_operations(self) -> list[dict[str, object]]:
        with self._lock:
            return [{"call_id": call_id, "operation": name,
                     "duration_seconds": time.monotonic() - started}
                    for call_id, (name, started) in self._pending.items()]

    def shell_result(
        self,
        *,
        command: str,
        cwd: str,
        exit_code: int | None,
        stdout: str = "",
        stderr: str = "",
        duration_seconds: float = 0.0,
        timed_out: bool = False,
    ) -> None:
        self.event(
            "shell_result",
            command=command,
            cwd=cwd,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=round(duration_seconds, 3),
            timed_out=timed_out,
        )
