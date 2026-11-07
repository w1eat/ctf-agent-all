"""Recover closing JSON delimiters without inventing structured result values."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError
from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability, RawOutput, WrapOutputValidateHandler
from pydantic_ai.output import OutputContext

logger = logging.getLogger(__name__)


def _complete_json_containers(text: str) -> str | None:
    closing = []
    in_string = escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "{[":
            closing.append("}" if char == "{" else "]")
        elif char in "}]" and (not closing or closing.pop() != char):
            return None
    if in_string or not closing:
        return None
    completed = text + "".join(reversed(closing))
    try:
        json.loads(completed)
    except (ValueError, RecursionError):
        return None
    return completed


class CompleteJSONOutput(AbstractCapability):
    async def wrap_output_validate(
        self, ctx: RunContext, *, output_context: OutputContext,
        output: RawOutput, handler: WrapOutputValidateHandler,
    ) -> Any:
        try:
            return await handler(output)
        except ValidationError as exc:
            if output_context.mode != "prompted" or not isinstance(output, str):
                raise
            if not any(error["type"] == "json_invalid" for error in exc.errors()):
                raise
            completed = _complete_json_containers(output)
            if completed is None:
                raise
            validated = await handler(completed)
            logger.info("Recovered structured output by completing closing JSON delimiters")
            return validated
