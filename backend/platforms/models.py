"""Normalized platform-facing domain models."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChallengeMode(StrEnum):
    ATTACHMENT = "attachment"
    REMOTE = "remote"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class ChallengeState(StrEnum):
    DISCOVERED = "discovered"
    WAITING_FOR_DECISION = "waiting_for_decision"
    PREPARING = "preparing"
    WAITING_FOR_PACKAGE = "waiting_for_package"
    WAITING_FOR_ENVIRONMENT = "waiting_for_environment"
    READY = "ready"
    RUNNING = "running"
    SOLVED = "solved"
    NEEDS_INPUT = "needs_input"
    FAILED = "failed"


class PlatformProfile(BaseModel):
    name: str = "unknown"
    origin: str
    authenticated: bool = False
    capabilities: set[str] = Field(default_factory=set)
    evidence: list[str] = Field(default_factory=list)


class EnvironmentInfo(BaseModel):
    status: str = "unknown"
    source: str = "remote"
    url: str = ""
    host: str = ""
    port: int | None = None
    compose_project: str = ""
    expires_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubmissionResult(BaseModel):
    status: str = "unknown"
    message: str = ""
    display: str = ""


@dataclass(frozen=True)
class AttachmentMetadata:
    """Canonical attachment metadata across platform API dialects."""

    attachment_id: str
    name: str
    source_url: str = ""
    target: str = ""
    challenge_page_url: str = ""
    size: int | None = None
    sha256: str = ""
    raw: dict[str, Any] | None = None

    @staticmethod
    def _first(data: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            value = data.get(key)
            if value not in (None, ""):
                return value
        return None

    @staticmethod
    def _normalize_source_url(source_url: str, attachment_id: str, has_explicit_id: bool) -> str:
        if not source_url or not has_explicit_id:
            return source_url
        parsed = urlsplit(source_url)
        if not parsed.scheme or not parsed.netloc:
            return source_url
        path = parsed.path.rstrip("/")
        if not re.search(r"/attachments$", path, re.IGNORECASE):
            return source_url
        path = f"{path}/{quote(attachment_id, safe='')}"
        return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    @classmethod
    def from_raw(cls, item: Any, index: int = 0) -> AttachmentMetadata:
        if isinstance(item, str):
            raw: dict[str, Any] = {"value": item}
            source_url = item if item.startswith(("http://", "https://")) else ""
            name = item.rsplit("/", 1)[-1] or f"attachment-{index}"
            explicit_id = False
            attachment_id = str(index)
            target = ""
            challenge_page_url = ""
            size = None
            sha256 = ""
        else:
            raw = dict(item or {})
            explicit = cls._first(raw, "id", "attachment_id")
            explicit_id = explicit is not None
            attachment_id = str(explicit if explicit is not None else index)
            name = str(cls._first(raw, "file_name", "fileName", "filename", "name") or f"attachment-{index}")
            source_url = str(cls._first(raw, "source_url", "url") or "")
            target = str(cls._first(raw, "target", "element") or "")
            challenge_page_url = str(raw.get("challenge_page_url") or "")
            raw_size = cls._first(raw, "byte_length", "byteLength", "size")
            try:
                size = int(raw_size) if raw_size is not None else None
            except (TypeError, ValueError):
                size = None
            sha256 = str(raw.get("sha256") or "").strip().casefold()
        source_url = cls._normalize_source_url(source_url, attachment_id, explicit_id)
        return cls(
            attachment_id=attachment_id,
            name=name,
            source_url=source_url,
            target=target,
            challenge_page_url=challenge_page_url,
            size=size,
            sha256=sha256,
            raw=raw,
        )

    @property
    def has_exact_source_url(self) -> bool:
        return bool(re.search(r"/attachments/[^/?#]+(?:[?#].*)?$", self.source_url, re.IGNORECASE))

    @property
    def is_collection_url(self) -> bool:
        return bool(re.search(r"/attachments/?(?:[?#].*)?$", self.source_url, re.IGNORECASE))


class ChallengeBundle(BaseModel):
    """Platform-neutral challenge representation used by coordinators and solvers."""

    model_config = ConfigDict(extra="allow")

    platform: str = "unknown"
    native_id: str
    name: str
    category: str = ""
    points: int = 0
    description: str = ""
    files: list[str] = Field(default_factory=list)
    mode: ChallengeMode = ChallengeMode.UNKNOWN
    connection_info: str = ""
    environment_required: bool = False
    challenge_url: str = ""
    environment: dict[str, Any] = Field(default_factory=dict)
    capabilities: set[str] = Field(default_factory=set)
    source_data: dict[str, Any] = Field(default_factory=dict)
    state: ChallengeState = ChallengeState.DISCOVERED
    reason: str = ""

    @field_validator("files", mode="before")
    @classmethod
    def normalize_files(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return [str(item) for item in value]

    def inferred_mode(self) -> ChallengeMode:
        has_files = bool(self.files or self.source_data.get("attachments"))
        has_remote = bool(self.environment_required or self.connection_info or self.environment)
        if has_files and has_remote:
            return ChallengeMode.HYBRID
        if has_files:
            return ChallengeMode.ATTACHMENT
        if has_remote:
            return ChallengeMode.REMOTE
        return ChallengeMode.UNKNOWN

    def normalized(self) -> ChallengeBundle:
        bundle = self
        updates: dict[str, ChallengeMode | ChallengeState] = {}
        if not isinstance(bundle.mode, ChallengeMode):
            try:
                updates["mode"] = ChallengeMode(bundle.mode)
            except (TypeError, ValueError):
                updates["mode"] = ChallengeMode.UNKNOWN
        if not isinstance(bundle.state, ChallengeState):
            try:
                updates["state"] = ChallengeState(bundle.state)
            except (TypeError, ValueError):
                updates["state"] = ChallengeState.DISCOVERED
        if updates:
            bundle = bundle.model_copy(update=updates)
        inferred = bundle.inferred_mode()
        return bundle if bundle.mode == inferred else bundle.model_copy(update={"mode": inferred})

    def metadata_dict(self) -> dict[str, Any]:
        """Return the stable YAML representation; runtime secrets are excluded."""
        bundle = self.normalized()
        return {
            "version": "beta2",
            "platform": bundle.platform,
            "native_id": bundle.native_id,
            "name": bundle.name,
            "category": bundle.category,
            "description": bundle.description,
            "value": bundle.points,
            "files": bundle.files,
            "challenge_mode": bundle.mode.value,
            "connection_info": bundle.connection_info,
            "environment_required": bundle.environment_required,
            "challenge_url": bundle.challenge_url,
            "environment": bundle.environment,
            "capabilities": sorted(bundle.capabilities),
            "attachments": bundle.source_data.get("attachments", []),
            "attachments_scanned": bool(bundle.source_data.get("attachments_scanned")),
            "state": bundle.state.value if isinstance(bundle.state, ChallengeState) else str(bundle.state),
            "reason": bundle.reason,
        }

    @classmethod
    def from_metadata(cls, data: dict[str, Any], *, platform: str = "local") -> ChallengeBundle:
        attachments = list(data.get("attachments", []) or [])
        files: list[str] = []
        for item in data.get("files", []) or []:
            if isinstance(item, str) and item.replace("\\", "/").startswith("distfiles/"):
                files.append(item.replace("\\", "/"))
                continue
            if isinstance(item, dict):
                attachments.append(item)
                continue
            if isinstance(item, str) and item.lstrip().startswith("{"):
                try:
                    legacy = ast.literal_eval(item)
                except (SyntaxError, ValueError):
                    legacy = None
                if isinstance(legacy, dict):
                    attachments.append(legacy)
        deduped_attachments: list[Any] = []
        seen_attachment_ids: set[str] = set()
        for index, attachment in enumerate(attachments):
            if isinstance(attachment, dict):
                identity = str(
                    attachment.get("id")
                    or attachment.get("attachment_id")
                    or attachment.get("source_url")
                    or attachment.get("url")
                    or f"index-{index}"
                )
            else:
                identity = str(attachment)
            if identity in seen_attachment_ids:
                continue
            seen_attachment_ids.add(identity)
            deduped_attachments.append(attachment)
        connection_info = data.get("connection_info", "") or ""
        environment = data.get("environment", {}) or {}
        environment_required = bool(
            data.get("environment_required", False)
            or connection_info
            or environment
        )
        return cls(
            platform=data.get("platform", platform),
            native_id=str(data.get("native_id", data.get("id", data.get("name", "")))),
            name=data.get("name", "Unknown"),
            category=data.get("category", ""),
            points=int(data.get("value", data.get("points", 0)) or 0),
            description=data.get("description", "") or "",
            files=files,
            mode=ChallengeMode.UNKNOWN,
            connection_info=connection_info,
            environment_required=environment_required,
            challenge_url=data.get("challenge_url", "") or "",
            environment=environment,
            capabilities=set(data.get("capabilities", []) or []),
            source_data={
                "attachments": deduped_attachments,
                "environment_required": environment_required,
                "attachments_scanned": bool(data.get("attachments_scanned")) or (
                    bool(deduped_attachments)
                    and all(
                        isinstance(item, dict)
                        and bool(
                            AttachmentMetadata.from_raw(item).target
                            or AttachmentMetadata.from_raw(item).challenge_page_url
                            or AttachmentMetadata.from_raw(item).has_exact_source_url
                        )
                        for item in deduped_attachments
                    )
                ),
            },
            state=data.get("state", ChallengeState.DISCOVERED),
            reason=data.get("reason", "") or "",
        ).normalized()
