"""Persistent, secret-free browser workflow recipes."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

SAVE_RECIPE_TOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "data": {
            "type": "object",
            "description": "Credential-free submission workflow. Use action/value and data.submit in each step.",
            "properties": {
                "platform_origin": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "description": "Navigate: action=navigate, value=same-origin URL with {challenge_id}. Input: action=type, target=CSS selector, value={flag}, data.submit=true only when Enter submits.",
                        "properties": {
                            "action": {"type": "string", "enum": ["navigate", "type", "fill", "click", "wait_for", "snapshot"]},
                            "target": {"type": "string", "description": "Stable CSS selector observed on the page"},
                            "value": {"type": "string"},
                            "data": {"type": "object", "properties": {"submit": {"type": "boolean"}}},
                            "type": {"type": "string", "description": "Legacy alias for action"},
                            "url": {"type": "string", "description": "Legacy alias for navigate value"},
                            "text": {"type": "string", "description": "Legacy alias for type value"},
                            "submit": {"type": "boolean", "description": "Legacy alias for data.submit"},
                        },
                        "anyOf": [{"required": ["action"]}, {"required": ["type"]}],
                    },
                },
                "success_markers": {"type": "array", "items": {"type": "string"}},
                "failure_markers": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["platform_origin", "steps"],
        }
    },
    "required": ["data"],
}


class RecipeStep(BaseModel):
    action: str
    target: str = ""
    value: str = ""
    data: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_step_aliases(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        step = dict(value)

        def move(alias: str, canonical: str) -> None:
            if alias not in step:
                return
            if canonical in step and step[canonical] != step[alias]:
                raise ValueError(f"conflicting {canonical} and {alias} fields")
            step[canonical] = step.pop(alias)

        move("type", "action")
        if step.get("action") == "navigate":
            move("url", "value")
        elif step.get("action") == "type":
            move("text", "value")
            if "submit" in step:
                data = dict(step.get("data") or {})
                if "submit" in data and data["submit"] != step["submit"]:
                    raise ValueError("conflicting submit and data.submit fields")
                data["submit"] = step.pop("submit")
                step["data"] = data
        return step

    @field_validator("target", mode="before")
    @classmethod
    def normalize_target(cls, value: Any) -> Any:
        """Accept a couple of common locator objects and persist a stable selector."""
        if isinstance(value, dict):
            selector = value.get("selector")
            if isinstance(selector, str) and selector.strip():
                return selector.strip()

            # Coordinators often express an accessible textbox as a Playwright
            # role/name locator. The browser MCP recipe format takes a string;
            # its target parameter accepts unique CSS selectors, so translate
            # the common aria-label-backed form before validating the recipe.
            role = str(value.get("role", "")).casefold()
            name = value.get("name")
            if role == "textbox" and isinstance(name, str) and name.strip():
                return f"[aria-label={json.dumps(name.strip(), ensure_ascii=False)}]"
        return value


class PlatformRecipe(BaseModel):
    platform_origin: str
    version: int = 1
    confidence: float = 0.0
    steps: list[RecipeStep] = Field(default_factory=list)
    success_markers: list[str] = Field(default_factory=list)
    failure_markers: list[str] = Field(default_factory=list)


class RecipeStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @staticmethod
    def key(origin: str) -> str:
        return hashlib.sha256(origin.rstrip("/").encode()).hexdigest()[:16]

    def path_for(self, origin: str) -> Path:
        return self.root / f"{self.key(origin)}.json"

    def load(self, origin: str) -> PlatformRecipe | None:
        path = self.path_for(origin)
        try:
            return PlatformRecipe.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save(self, recipe: PlatformRecipe) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.path_for(recipe.platform_origin)
        path.write_text(recipe.model_dump_json(indent=2), encoding="utf-8")
        return path


def submission_recipe_issue(recipe: PlatformRecipe | None, origin: str) -> str | None:
    """Reject recipes that cannot submit a flag for the configured platform."""
    if recipe is None:
        return "No submit recipe is available for this platform"
    if recipe.platform_origin.rstrip("/") != origin.rstrip("/"):
        return "Submit recipe origin does not match the configured platform URL"
    if not recipe.steps:
        return "Submit recipe has no browser steps"

    expected = urlparse(origin)
    navigations = [
        (index, step.value or step.data.get("url", ""))
        for index, step in enumerate(recipe.steps) if step.action == "navigate"
    ]
    if not navigations or not any("{challenge_id}" in str(url) for _, url in navigations):
        return "Submit recipe needs a challenge-specific navigate step with {challenge_id}"
    if any(
        (urlparse(str(url)).scheme, urlparse(str(url)).netloc)
        != (expected.scheme, expected.netloc)
        for _, url in navigations
    ):
        return "Submit recipe navigation must stay on the configured platform origin"

    def inputs_flag(step: RecipeStep) -> bool:
        if step.action == "type":
            return step.value == "{flag}" and bool(step.target or step.data.get("target"))
        if step.action == "fill":
            return any(
                field.get("value") == "{flag}" and bool(field.get("target"))
                for field in step.data.get("fields", []) if isinstance(field, dict)
            )
        return False

    input_indices = [index for index, step in enumerate(recipe.steps) if inputs_flag(step)]
    if not input_indices:
        return "Submit recipe needs a visible input step with the {flag} placeholder"

    def submits_after_input(index: int, step: RecipeStep) -> bool:
        if step.action == "click" and (step.target or step.data.get("target")):
            return any(
                nav_index < input_index < index
                for nav_index, _ in navigations for input_index in input_indices
            )
        # Playwright's browser_type supports submit=True, which presses Enter
        # after typing. This is the complete submit action for textarea-based CTF UIs.
        if step.action == "type" and inputs_flag(step) and step.data.get("submit") is True:
            return any(nav_index < index for nav_index, _ in navigations)
        return False

    if not any(submits_after_input(index, step) for index, step in enumerate(recipe.steps)):
        return "Submit recipe needs a submit-button click after entering the flag or an Enter-enabled flag input"
    return None


def redact_sensitive_text(value: str) -> str:
    """Remove common auth material before writing browser evidence or recipes."""
    value = re.sub(r"(?i)(authorization|cookie|set-cookie|token|password)\s*[:=]\s*[^,\r\n]+", r"\1=<redacted>", value)
    value = re.sub(
        r'''(?i)(["']?(?:authorization|cookie|set-cookie|token|password)["']?\s*[:=]\s*["']?)[^,\s"'}]+''',
        r"\1<redacted>",
        value,
    )
    value = re.sub(r"(?i)bearer\s+[A-Za-z0-9._-]+", "Bearer <redacted>", value)
    return value
