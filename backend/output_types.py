"""Structured output types for solver agents."""

from pydantic import BaseModel, Field


class FlagFound(BaseModel):
    type: str = "flag_found"
    flag: str
    method: str  # brief description of how
    evidence: list[str] = Field(default_factory=list)
    solution_steps: list[str] = Field(default_factory=list)
    exp_paths: list[str] = Field(default_factory=list)
    exp_run_command: str = ""
    artifact_paths: list[str] = Field(default_factory=list, description="实际生成的关键图片、截图、音频或文本证据，位于 /challenge/workspace/ 下")


class CandidateFound(BaseModel):
    """A proposed flag that still requires independent verification."""

    type: str = "candidate_found"
    flag: str
    method: str
    evidence: list[str] = Field(default_factory=list)
    solution_steps: list[str] = Field(default_factory=list)
    exp_paths: list[str] = Field(default_factory=list)
    exp_run_command: str = ""
    artifact_paths: list[str] = Field(default_factory=list, description="实际生成的关键图片、截图、音频或文本证据，位于 /challenge/workspace/ 下")


class SolverBlocked(BaseModel):
    type: str = "blocked"
    reason: str
    message: str = ""
    required: list[str] = Field(default_factory=list)


class SolverNeedsInput(BaseModel):
    type: str = "needs_input"
    reason: str
    message: str = ""
    required: list[str] = Field(default_factory=list)


class SolverGaveUp(BaseModel):
    """An unfinished attempt with concrete findings for the next attempt."""

    type: str = "gave_up"
    findings_summary: str


SolverOutput = FlagFound | CandidateFound | SolverBlocked | SolverNeedsInput | SolverGaveUp


def solver_output_json_schema() -> dict:
    """JSON schema for solver structured output — shared by Claude SDK and Codex.

    Solvers may return a flag, a structured blocked/needs_input result,
    or findings from an unfinished attempt.
    No free-form final text is accepted as a solver result.
    """
    return {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "type": {"const": "flag_found"},
                    "flag": {"type": "string"},
                    "method": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "solution_steps": {"type": "array", "items": {"type": "string"}},
                    "exp_paths": {"type": "array", "items": {"type": "string"}},
                    "exp_run_command": {"type": "string"},
                    "artifact_paths": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["type", "flag", "method"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "type": {"const": "candidate_found"},
                    "flag": {"type": "string"},
                    "method": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "solution_steps": {"type": "array", "items": {"type": "string"}},
                    "exp_paths": {"type": "array", "items": {"type": "string"}},
                    "exp_run_command": {"type": "string"},
                    "artifact_paths": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["type", "flag", "method"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "type": {"enum": ["blocked", "needs_input"]},
                    "reason": {"type": "string"},
                    "message": {"type": "string"},
                    "required": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["type", "reason", "message", "required"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {
                    "type": {"const": "gave_up"},
                    "findings_summary": {"type": "string"},
                },
                "required": ["type", "findings_summary"],
                "additionalProperties": False,
            },
        ]
    }
