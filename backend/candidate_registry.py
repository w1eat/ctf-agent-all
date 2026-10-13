"""Candidate Flag registry and independent-verification bookkeeping.

The registry deliberately lives outside individual model backends.  A model
may suggest a value, but only the swarm can decide whether the value has enough
independent evidence to terminate the challenge.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


def normalize_flag(value: str | None) -> str:
    """Normalize harmless transport differences without changing the payload."""
    # Only trim transport whitespace. Internal spaces may be meaningful in a
    # challenge-specific answer and must never be silently rewritten.
    return str(value or "").strip()


@dataclass
class CandidateRecord:
    flag: str
    first_source: str
    method: str = ""
    evidence: list[str] = field(default_factory=list)
    sources: set[str] = field(default_factory=set)
    accepted_sources: set[str] = field(default_factory=set)
    rejected_sources: set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def verification_count(self) -> int:
        return len(self.accepted_sources)

    @property
    def rejected(self) -> bool:
        return bool(self.rejected_sources) and not self.accepted_sources


class CandidateRegistry:
    """Thread-safe-at-the-event-loop candidate registry.

    Swarm methods are async and therefore serialize updates on the event loop;
    no model backend is allowed to mutate records directly.
    """

    def __init__(self, quorum: int = 2) -> None:
        self.quorum = max(1, int(quorum))
        self.records: dict[str, CandidateRecord] = {}

    def propose(
        self,
        flag: str,
        source: str,
        *,
        method: str = "",
        evidence: list[str] | tuple[str, ...] = (),
    ) -> CandidateRecord | None:
        normalized = normalize_flag(flag)
        if not normalized:
            return None
        record = self.records.get(normalized)
        if record is None:
            record = CandidateRecord(
                flag=normalized,
                first_source=source,
                method=method[:500],
                evidence=[str(item)[:1000] for item in evidence][:20],
            )
            self.records[normalized] = record
        record.sources.add(source)
        record.updated_at = time.time()
        for item in evidence:
            value = str(item)[:1000]
            if value and value not in record.evidence:
                record.evidence.append(value)
        return record

    def verify(
        self,
        flag: str,
        verifier: str,
        *,
        accepted: bool,
        evidence: list[str] | tuple[str, ...] = (),
    ) -> CandidateRecord | None:
        normalized = normalize_flag(flag)
        record = self.records.get(normalized)
        if record is None:
            return None
        record.updated_at = time.time()
        record.sources.add(verifier)
        if accepted:
            record.accepted_sources.add(verifier)
        else:
            record.rejected_sources.add(verifier)
        for item in evidence:
            value = str(item)[:1000]
            if value and value not in record.evidence:
                record.evidence.append(value)
        return record

    def verified(self, flag: str) -> CandidateRecord | None:
        record = self.records.get(normalize_flag(flag))
        if record and record.verification_count >= self.quorum:
            return record
        return None

    def snapshot(self) -> list[dict[str, object]]:
        return [
            {
                "flag": record.flag,
                "first_source": record.first_source,
                "sources": sorted(record.sources),
                "accepted_sources": sorted(record.accepted_sources),
                "rejected_sources": sorted(record.rejected_sources),
                "verification_count": record.verification_count,
                "verified": record.verification_count >= self.quorum,
                "evidence": list(record.evidence),
            }
            for record in self.records.values()
        ]
