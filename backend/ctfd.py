"""CTFd client — async httpx, token + session auth."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36"


@dataclass
class CTFdClient:
    base_url: str = "http://localhost:8000"
    token: str = ""
    username: str = "admin"
    password: str = "admin"

    _client: httpx.AsyncClient | None = field(default=None, repr=False)
    _csrf_token: str = ""
    _logged_in: bool = False
    _challenge_ids: dict[str, int] = field(default_factory=dict)

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            # verify=False: CTFd instances often use self-signed certs or HTTP.
            # This is a CTF tool, not production infrastructure.
            self._client = httpx.AsyncClient(
                base_url=self.base_url.rstrip("/"),
                follow_redirects=False,
                verify=False,
                timeout=30.0,
                headers={"User-Agent": USER_AGENT},
            )
        return self._client

    async def _ensure_logged_in(self) -> None:
        if self._logged_in or self.token:
            return
        client = await self._ensure_client()

        # GET login page for nonce
        resp = await client.get("/login")
        m = re.search(r'id="nonce"[^>]*value="([^"]+)"', resp.text)
        if not m:
            m = re.search(r'name="nonce"[^>]*value="([^"]+)"', resp.text)
        if not m:
            raise RuntimeError("Could not find nonce on CTFd login page")
        nonce = m.group(1)

        # POST credentials
        resp = await client.post(
            "/login",
            data={
                "name": self.username,
                "password": self.password,
                "_submit": "Submit",
                "nonce": nonce,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code == 200:
            raise RuntimeError("CTFd login failed — bad credentials")
        self._logged_in = True

    async def _get_csrf(self) -> str:
        if self._csrf_token:
            return self._csrf_token
        client = await self._ensure_client()
        resp = await client.get("/challenges")
        m = re.search(r"csrfNonce':\s*\"([A-Fa-f0-9]+)\"", resp.text)
        if not m:
            raise RuntimeError("Could not find csrfNonce on CTFd challenges page")
        self._csrf_token = m.group(1)
        return self._csrf_token

    def _base_headers(self) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self.token:
            token = self.token.strip()
            for prefix in ("Bearer ", "Token "):
                if token.lower().startswith(prefix.lower()):
                    token = token[len(prefix):].strip()
                    break
            h["Authorization"] = f"Token {token}"
        return h

    async def _get(self, path: str) -> Any:
        await self._ensure_logged_in()
        client = await self._ensure_client()
        resp = await client.get(f"/api/v1{path}", headers=self._base_headers())
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, body: dict[str, Any]) -> Any:
        await self._ensure_logged_in()
        client = await self._ensure_client()
        headers = self._base_headers()
        if not self.token:
            headers["CSRF-Token"] = await self._get_csrf()
        resp = await client.post(
            f"/api/v1{path}",
            json=body,
            headers=headers,
        )
        # Retry once on 403 — CSRF token may have gone stale
        if resp.status_code == 403 and not self.token:
            self._csrf_token = ""
            headers["CSRF-Token"] = await self._get_csrf()
            resp = await client.post(
                f"/api/v1{path}",
                json=body,
                headers=headers,
            )
        resp.raise_for_status()
        return resp.json()

    async def fetch_challenge_stubs(self) -> list[dict[str, Any]]:
        """Fetch lightweight challenge list (no per-challenge detail fetch)."""
        data = await self._get("/challenges?per_page=500")
        return [ch for ch in data.get("data", []) if ch.get("type") != "hidden"]

    async def get_challenge_id(self, name: str) -> int:
        if name in self._challenge_ids:
            return self._challenge_ids[name]

        data = await self._get("/challenges?per_page=500")
        for ch in data.get("data", []):
            self._challenge_ids[ch["name"]] = ch["id"]

        if name not in self._challenge_ids:
            raise RuntimeError(f'Challenge "{name}" not found in CTFd')
        return self._challenge_ids[name]

    async def fetch_all_challenges(self) -> list[dict[str, Any]]:
        data = await self._get("/challenges?per_page=500")
        challenges = []
        for stub in data.get("data", []):
            if stub.get("type") == "hidden":
                continue
            detail = await self._get(f"/challenges/{stub['id']}")
            challenges.append(detail["data"])
        return challenges

    async def fetch_solved_names(self) -> set[str]:
        try:
            me = await self._get("/users/me")
            user_data = me.get("data", {})
            # Use team solves if on a team, otherwise user solves
            team_id = user_data.get("team_id")
            if team_id:
                solves = await self._get(f"/teams/{team_id}/solves")
            else:
                user_id = user_data.get("id")
                if not user_id:
                    return set()
                solves = await self._get(f"/users/{user_id}/solves")
            return {
                s["challenge"]["name"]
                for s in solves.get("data", [])
                if s.get("challenge", {}).get("name")
            }
        except Exception as exc:
            raise RuntimeError("Could not fetch solved challenges from CTFd") from exc

    async def pull_challenge(self, challenge: dict[str, Any], output_dir: str) -> str:
        """Download a challenge's distfiles and write metadata.yml.

        Returns the challenge directory path.
        """
        from pathlib import Path
        from urllib.parse import unquote, urlparse
        from uuid import uuid4

        import yaml

        name = challenge.get("name", f"challenge-{challenge['id']}")
        # Slugify
        slug = re.sub(r'[<>:"/\\|?*.\x00-\x1f]', "", name.lower().strip())
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-") or "challenge"

        ch_dir = Path(output_dir) / slug
        ch_dir.mkdir(parents=True, exist_ok=True)

        # Download distfiles using the logged-in session
        await self._ensure_logged_in()
        client = await self._ensure_client()
        downloaded_files: list[str] = []
        used_names: set[str] = set()
        for index, raw_url in enumerate(challenge.get("files") or []):
            dist_dir = ch_dir / "distfiles"
            dist_dir.mkdir(exist_ok=True)
            url = raw_url if raw_url.startswith("http") else f"{self.base_url.rstrip('/')}/{raw_url.lstrip('/')}"
            url_path = urlparse(url).path
            candidate = unquote(url_path.rstrip("/").rsplit("/", 1)[-1])
            fname = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", candidate).strip(" .")
            if not fname:
                fname = f"attachment-{index + 1}"
            if fname.split(".", 1)[0].upper() in {
                "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10)),
            }:
                fname = f"attachment-{index + 1}-{fname}"
            stem, suffix = Path(fname).stem, Path(fname).suffix
            counter = index + 1
            while fname.casefold() in used_names:
                fname = f"{stem}-{counter}{suffix}"
                counter += 1
            used_names.add(fname.casefold())
            dest = dist_dir / fname
            temporary = dist_dir / f".{fname}.{uuid4().hex}.part"
            try:
                # Only send auth headers to our CTFd server
                headers = self._base_headers() if urlparse(url).hostname == urlparse(self.base_url).hostname else {}
                resp = await client.get(
                    url, headers=headers,
                    follow_redirects=True, timeout=60.0,
                )
                resp.raise_for_status()
                temporary.write_bytes(resp.content)
                temporary.replace(dest)
                downloaded_files.append(f"distfiles/{fname}")
                logger.info("Downloaded: %s (%d bytes)", fname, len(resp.content))
            except Exception as exc:
                temporary.unlink(missing_ok=True)
                raise RuntimeError(f"Failed to download CTFd attachment {url}: {exc}") from exc

        # Write metadata.yml
        from markdownify import markdownify as html2md

        desc = challenge.get("description") or ""
        try:
            desc = html2md(desc, heading_style="atx", escape_asterisks=False)
        except Exception:
            pass

        tags = [t["value"] if isinstance(t, dict) else str(t) for t in (challenge.get("tags") or [])]
        meta = {
            "name": name,
            "category": challenge.get("category", ""),
            "description": desc.strip(),
            "value": challenge.get("value", 0),
            "connection_info": challenge.get("connection_info") or "",
            "tags": tags,
            "solves": challenge.get("solves", 0),
            "files": downloaded_files,
        }
        # Add hints
        hints = []
        for h in challenge.get("hints") or []:
            hint = {"cost": h.get("cost", 0)}
            if h.get("content"):
                hint["content"] = h["content"]
            hints.append(hint)
        if hints:
            meta["hints"] = hints

        (ch_dir / "metadata.yml").write_text(
            yaml.dump(meta, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

        return str(ch_dir)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
