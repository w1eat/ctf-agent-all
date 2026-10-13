import pytest
from pydantic import ValidationError
from pydantic_ai import PromptedOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.usage import RunUsage

from backend.agents.solver import _output_type_for_model
from backend.config import Settings
from backend.cost_tracker import calc_cost
from backend.models import (
    context_window,
    provider_from_spec,
    resolve_model,
    resolve_model_settings,
    supports_vision,
)


def test_deepseek_flash_resolves_to_openai_compatible_model() -> None:
    model = resolve_model(
        "deepseek/deepseek-flash",
        Settings(_env_file=None, deepseek_api_key="test-key"),
    )

    assert isinstance(model, OpenAIChatModel)
    assert str(model.client.base_url) == "https://api.deepseek.com"
    assert model.profile["openai_chat_thinking_field"] == "reasoning_content"
    assert model.profile["openai_chat_supports_max_completion_tokens"] is False
    assert model.profile["supports_json_schema_output"] is False
    assert model.profile["default_structured_output_mode"] == "prompted"
    assert model.profile["openai_supports_tool_choice_required"] is False
    assert model.profile["openai_supports_forced_tool_choice_with_thinking"] is False
    assert resolve_model_settings("deepseek/deepseek-flash")["tool_choice"] == "auto"
    assert supports_vision("deepseek/deepseek-flash") is True
    assert isinstance(_output_type_for_model("deepseek/deepseek-flash"), PromptedOutput)


def test_non_deepseek_keeps_native_structured_output_type() -> None:
    from backend.output_types import FlagFound, SolverBlocked, SolverNeedsInput

    output_type = _output_type_for_model("openai/gpt-5.6-luna")
    assert FlagFound in output_type.__args__
    assert SolverBlocked in output_type.__args__
    assert SolverNeedsInput in output_type.__args__


def test_deepseek_reasoner_keeps_reasoning_compatibility_profile() -> None:
    model = resolve_model(
        "deepseek/deepseek-reasoner",
        Settings(_env_file=None, deepseek_api_key="test-key"),
    )

    assert model.profile["thinking_always_enabled"] is True
    assert model.profile["openai_supports_tool_choice_required"] is False
    assert model.profile["default_structured_output_mode"] == "prompted"
    assert resolve_model_settings("deepseek/deepseek-reasoner")["tool_choice"] == "auto"
    assert supports_vision("deepseek/deepseek-reasoner") is False


def test_deepseek_model_metadata_and_cost_tracking() -> None:
    spec = "deepseek/deepseek-flash"
    assert provider_from_spec(spec) == "deepseek"
    assert context_window(spec) == 1_000_000
    assert resolve_model_settings(spec) == {"max_tokens": 128_000, "tool_choice": "auto"}
    assert calc_cost(
        RunUsage(input_tokens=1000, output_tokens=1000),
        "deepseek-flash",
        provider_spec="deepseek",
    ) > 0


def test_generic_openai_compatible_model_preserves_slash_name() -> None:
    model = resolve_model(
        "openai/THUDM/GLM-4-9B-0414",
        Settings(
            _env_file=None,
            api_key="test-key",
            base_url="https://api.siliconflow.cn/v1",
        ),
    )

    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "THUDM/GLM-4-9B-0414"
    assert str(model.client.base_url) == "https://api.siliconflow.cn/v1/"


@pytest.mark.parametrize(
    "field",
    ["max_concurrent_challenges", "max_attempts_per_challenge", "preparation_concurrency"],
)
def test_solver_limits_must_be_positive(field: str) -> None:
    with pytest.raises(ValidationError, match="positive integer"):
        Settings(_env_file=None, **{field: 0})
