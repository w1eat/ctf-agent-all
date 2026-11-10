"""Correlated requests from solvers to the coordinator for one run."""

from __future__ import annotations

import asyncio
import json
import math
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class _CoordinatorRequest:
    request_id: str
    challenge_name: str
    model_spec: str
    message: str
    deadline: float
    future: asyncio.Future[dict[str, str]]
    cancel_event: asyncio.Event | None = None
    state: str = "queued"
    response: str = ""
    wait_finished: bool = False
    last_announcement: float | None = None
    announcement_count: int = 0

    def result(self) -> dict[str, str]:
        return {"request_id": self.request_id, "status": self.state, "response": self.response}

    def as_dict(self, *, include_message: bool = True) -> dict[str, Any]:
        result = {
            **self.result(),
            "challenge_name": self.challenge_name,
            "model_spec": self.model_spec,
            "remaining_seconds": max(0, math.ceil(self.deadline - time.monotonic())),
            "wait_finished": self.wait_finished,
        }
        if include_message:
            result["message"] = self.message
        return result


class CoordinatorRequestBroker:
    """Track solver requests independently of how long a solver waits for them."""

    def __init__(self) -> None:
        self._requests: dict[str, _CoordinatorRequest] = {}
        self._closed = False
        self._wakeup: Callable[[], None] | None = None

    def set_wakeup(self, wakeup: Callable[[], None]) -> None:
        self._wakeup = wakeup

    @staticmethod
    def _finish(request: _CoordinatorRequest, status: str, response: str) -> None:
        request.state = status
        request.response = response
        if not request.future.done():
            request.future.set_result(request.result())

    def _expire_queued(self) -> None:
        now = time.monotonic()
        for request in self._requests.values():
            if request.state != "queued":
                continue
            if request.cancel_event and request.cancel_event.is_set():
                self._finish(request, "cancelled", "The solver was cancelled before the request was claimed.")
            elif now >= request.deadline:
                self._finish(request, "not_started", "The request expired before the coordinator claimed it.")

    async def request(
        self,
        challenge_name: str,
        model_spec: str,
        message: str,
        *,
        timeout_seconds: float,
        cancel_event: asyncio.Event | None = None,
    ) -> dict[str, str]:
        if self._closed:
            return {"status": "unavailable", "response": "The coordinator is not running."}
        if not isinstance(message, str) or not message.strip():
            return {"status": "invalid_request", "response": "The request message is empty."}
        if timeout_seconds <= 0:
            return {"status": "invalid_request", "response": "The request timeout must be positive."}
        if cancel_event is not None and cancel_event.is_set():
            return {"status": "cancelled", "response": "The solver has been cancelled."}

        self._expire_queued()
        for existing in self._requests.values():
            if (existing.challenge_name, existing.model_spec, existing.message) == (
                challenge_name, model_spec, message
            ) and existing.state in {"queued", "in_progress", "unknown"}:
                return existing.result()

        request_id = uuid.uuid4().hex
        future = asyncio.get_running_loop().create_future()
        request = _CoordinatorRequest(
            request_id=request_id,
            challenge_name=challenge_name,
            model_spec=model_spec,
            message=message,
            deadline=time.monotonic() + timeout_seconds,
            future=future,
            cancel_event=cancel_event,
        )
        self._requests[request_id] = request
        cancel_waiter = asyncio.create_task(cancel_event.wait()) if cancel_event is not None else None
        waiters = {future, cancel_waiter} if cancel_waiter is not None else {future}
        try:
            if self._wakeup is not None:
                self._wakeup()
            done, _ = await asyncio.wait(waiters, timeout=timeout_seconds, return_when=asyncio.FIRST_COMPLETED)
            if future in done:
                return future.result()
            if cancel_waiter is not None and cancel_waiter in done:
                if request.state == "queued":
                    self._finish(request, "cancelled", "The solver was cancelled before the request was claimed.")
                return {
                    "request_id": request_id,
                    "status": "cancelled",
                    "response": "The solver was cancelled; a claimed action may still be running. Check its outcome before retrying.",
                }
            if request.state == "queued":
                self._finish(request, "not_started", "The request expired before the coordinator claimed it.")
                return request.result()
            return {
                "request_id": request_id,
                "status": "in_progress",
                "response": "The coordinator claimed this request but has not replied. Check its status before retrying.",
            }
        except asyncio.CancelledError:
            if request.state == "queued":
                self._finish(request, "cancelled", "The solver stopped waiting before the request was claimed.")
            raise
        finally:
            request.wait_finished = True
            if not future.done():
                future.cancel()
            if cancel_waiter is not None:
                cancel_waiter.cancel()
                await asyncio.gather(cancel_waiter, return_exceptions=True)

    def pending(self) -> list[dict[str, Any]]:
        self._expire_queued()
        return [request.as_dict(include_message=request.state != "queued") for request in self._requests.values()
                if request.state in {"queued", "in_progress", "unknown"}]

    def announcements(self, reminder_seconds: float = 30) -> list[dict[str, Any]]:
        """Remind the coordinator about queued and claimed requests without restarting them."""
        self._expire_queued()
        now = time.monotonic()
        result = []
        for request in self._requests.values():
            if request.state not in {"queued", "in_progress"}:
                continue
            if request.last_announcement is None or now - request.last_announcement >= reminder_seconds:
                request.last_announcement = now
                announcement = request.as_dict(include_message=request.state != "queued")
                announcement["reminder"] = request.announcement_count > 0
                request.announcement_count += 1
                result.append(announcement)
        return result

    def claim(self, request_id: str, challenge_name: str, model_spec: str) -> dict[str, str]:
        self._expire_queued()
        request = self._requests.get(request_id)
        if request is None:
            return {"status": "not_pending", "request_id": request_id}
        if (request.challenge_name, request.model_spec) != (challenge_name, model_spec):
            return {"status": "identity_mismatch", "request_id": request_id}
        if self._closed or request.state not in {"queued", "in_progress"}:
            return {"status": "not_pending", "request_id": request_id}
        if request.state == "in_progress":
            return {"status": "already_claimed", "request_id": request_id}
        request.state = "in_progress"
        request.response = "The coordinator has claimed this request."
        return {"status": "claimed", "request_id": request_id, "message": request.message}

    def reply(
        self, request_id: str, challenge_name: str, model_spec: str, status: str, response: str
    ) -> dict[str, str]:
        self._expire_queued()
        request = self._requests.get(request_id)
        if request is None:
            return {"status": "not_pending", "request_id": request_id}
        if (request.challenge_name, request.model_spec) != (challenge_name, model_spec):
            return {"status": "identity_mismatch", "request_id": request_id}
        if status not in {"answered", "blocked", "unknown"} or not isinstance(response, str):
            return {"status": "invalid_reply", "request_id": request_id}
        if request.state == "queued":
            return {"status": "not_claimed", "request_id": request_id}
        if request.state not in {"in_progress", "unknown"} or (request.state == "unknown" and status == "unknown"):
            return {"status": "not_pending", "request_id": request_id}

        if not request.wait_finished and time.monotonic() >= request.deadline and not request.future.done():
            request.future.set_result({
                "request_id": request_id,
                "status": "in_progress",
                "response": "The coordinator claimed this request but the wait expired. Check its status before retrying.",
            })
        delivery = "stored" if request.wait_finished or request.future.done() else "delivered"
        self._finish(request, status, response)
        return {"status": delivery, "request_id": request_id}

    def check(self, challenge_name: str, model_spec: str, request_id: str = "") -> Any:
        """Return only requests belonging to the calling solver, including late replies."""
        self._expire_queued()
        if not request_id:
            return [{
                "request_id": request.request_id,
                "status": request.state,
                "message_preview": request.message[:240],
                "wait_finished": request.wait_finished,
            } for request in self._requests.values()
                if (request.challenge_name, request.model_spec) == (challenge_name, model_spec)]
        request = self._requests.get(request_id)
        if request is None or (request.challenge_name, request.model_spec) != (challenge_name, model_spec):
            return {"status": "not_found", "request_id": request_id}
        return request.as_dict()

    def close(self) -> None:
        self._closed = True
        for request in self._requests.values():
            if request.state == "queued":
                self._finish(request, "unavailable", "The coordinator stopped before claiming the request.")
            elif request.state == "in_progress":
                self._finish(request, "unknown", "The coordinator stopped after claiming the request; check the action outcome before retrying.")


async def call_coordinator(request_fn, message: str) -> str:
    """Serialize the same result for every solver backend."""
    if request_fn is None:
        result = {"status": "unavailable", "response": "No coordinator is connected."}
    else:
        result = await request_fn(message)
    return json.dumps(result, ensure_ascii=False)


async def check_coordinator(check_fn, request_id: str = "") -> str:
    if check_fn is None:
        result = {"status": "unavailable", "response": "No coordinator is connected."}
    else:
        result = await check_fn(request_id)
    return json.dumps(result, ensure_ascii=False)


def make_claude_coordination_server(request_fn, check_fn=None):
    """Expose the same request tools through Claude Agent SDK's MCP server."""
    from claude_agent_sdk import create_sdk_mcp_server, tool

    @tool(
        "request_coordinator",
        "Ask the coordinator to perform a concrete action or provide information, and wait for its reply.",
        {"message": str},
    )
    async def request_coordinator(args: dict) -> dict:
        result = await call_coordinator(request_fn, args.get("message", ""))
        return {"content": [{"type": "text", "text": result}]}

    @tool(
        "check_coordinator_request",
        "Check one coordinator request by ID, or list this solver's requests with an empty ID.",
        {"request_id": str},
    )
    async def check_coordinator_request(args: dict) -> dict:
        result = await check_coordinator(check_fn, args.get("request_id", ""))
        return {"content": [{"type": "text", "text": result}]}

    return create_sdk_mcp_server("coordination", tools=[request_coordinator, check_coordinator_request])
