"""Model resolution — Bedrock, OpenAI-compatible APIs, and Google AI Studio."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import boto3
from google.genai.types import ThinkingLevel
from pydantic_ai.models import Model
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

if TYPE_CHECKING:
    from backend.config import Settings

# Default model specs — claude-sdk and codex providers use the new solver backends
DEFAULT_MODELS: list[str] = [
    "claude-sdk/claude-opus-4-6/medium",
    "claude-sdk/claude-opus-4-6/max",
    "codex/gpt-5.4",
    "codex/gpt-5.4-mini",
    "codex/gpt-5.3-codex",
]

# Context window sizes (tokens)
CONTEXT_WINDOWS: dict[str, int] = {
    "us.anthropic.claude-opus-4-6-v1": 1_000_000,
    "claude-opus-4-6": 1_000_000,
    "gpt-5.4": 1_000_000,
    "gpt-5.4-mini": 400_000,
    "gpt-5.3-codex": 1_000_000,
    "gpt-5.3-codex-spark": 128_000,
    "gemini-3-flash-preview": 1_000_000,
    "deepseek-flash": 1_000_000,
    # Kept for compatibility with older DeepSeek API model names.
    "deepseek-chat": 64_000,
    "deepseek-reasoner": 64_000,
}

# Models that support vision
VISION_MODELS: set[str] = {
    "us.anthropic.claude-opus-4-6-v1",
    "claude-opus-4-6",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gemini-3-flash-preview",
    "deepseek-flash",
}


def _deepseek_profile(model_id: str) -> OpenAIModelProfile:
    """Describe DeepSeek's Chat Completions compatibility quirks."""
    profile = OpenAIModelProfile(
        # DeepSeek reasoning responses use this non-standard OpenAI field. Keeping it in
        # the assistant history is required when a reasoning model calls tools.
        openai_chat_thinking_field="reasoning_content",
        openai_chat_send_back_thinking_parts="field",
        # DeepSeek uses the older max_tokens field and does not accept strict tool schemas.
        openai_chat_supports_max_completion_tokens=False,
        openai_supports_strict_tool_definition=False,
        # Chat Completions currently supports JSON mode, but not OpenAI's json_schema mode.
        supports_json_schema_output=False,
        supports_json_object_output=True,
        # DeepSeek Thinking rejects forced tool choices. Use prompted JSON for the final
        # structured output so the solver can keep regular tools available with auto choice.
        default_structured_output_mode="prompted",
        openai_supports_tool_choice_required=False,
        openai_supports_forced_tool_choice_with_thinking=False,
        supports_thinking=True,
    )
    if model_id == "deepseek-reasoner" or model_id.startswith("deepseek-r1"):
        profile.update(
            {
                "thinking_always_enabled": True,
            }
        )
    return profile


def resolve_model(spec: str, settings: Settings) -> Model:
    """Resolve a 'provider/model_id' spec to a Pydantic AI Model."""
    provider = provider_from_spec(spec)
    model_id = model_id_from_spec(spec)
    match provider:
        case "bedrock":
            if settings.aws_bearer_token:
                return BedrockConverseModel(
                    model_id,
                    provider=BedrockProvider(
                        api_key=settings.aws_bearer_token,
                        region_name=settings.aws_region,
                    ),
                )
            else:
                session = boto3.Session()
                client = session.client("bedrock-runtime", region_name=settings.aws_region)
                return BedrockConverseModel(
                    model_id,
                    provider=BedrockProvider(bedrock_client=client),
                )
        case "azure":
            return OpenAIChatModel(
                model_id,
                provider=OpenAIProvider(
                    base_url=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                ),
            )
        case "deepseek":
            return OpenAIChatModel(
                model_id,
                provider=OpenAIProvider(
                    base_url=settings.base_url or settings.deepseek_base_url,
                    api_key=settings.api_key or settings.deepseek_api_key,
                ),
                profile=_deepseek_profile(model_id),
            )
        case "openai":
            if not settings.base_url:
                raise ValueError("BASE_URL is required for the generic openai provider")
            return OpenAIChatModel(
                model_id,
                provider=OpenAIProvider(
                    base_url=settings.base_url,
                    api_key=settings.api_key,
                ),
            )
        case "zen":
            return OpenAIChatModel(
                model_id,
                provider=OpenAIProvider(
                    base_url="https://opencode.ai/zen/v1",
                    api_key=settings.opencode_zen_api_key,
                ),
            )
        case "google":
            return GoogleModel(
                model_id,
                provider=GoogleProvider(api_key=settings.gemini_api_key),
            )
        case "claude-sdk" | "codex":
            raise ValueError(
                f"Provider '{provider}' uses its own solver backend, not Pydantic AI. "
                f"resolve_model() should not be called for {spec}."
            )
        case _:
            raise ValueError(f"Unknown provider: {provider}")


def resolve_model_settings(spec: str) -> ModelSettings:
    """Get provider-specific model settings with caching enabled."""
    provider = spec.split("/", 1)[0]
    match provider:
        case "bedrock":
            return BedrockModelSettings(
                max_tokens=128_000,
                bedrock_cache_instructions=True,
                bedrock_cache_tool_definitions=True,
                bedrock_cache_messages=True,
            )
        case "azure" | "deepseek" | "openai" | "zen":
            # OpenAI-compatible providers use chat completions — server-side prompt caching
            # is automatic, no explicit config needed. Set max_tokens to avoid
            # reserving the full context window.
            settings: OpenAIChatModelSettings = {"max_tokens": 128_000}
            if provider == "deepseek":
                # DeepSeek rejects tool_choice=required while Thinking is active.
                settings["tool_choice"] = "auto"
            return settings
        case "google":
            return GoogleModelSettings(
                max_tokens=64_000,
                google_thinking_config={
                    "thinking_level": ThinkingLevel.HIGH,
                    "include_thoughts": True,
                },
            )
        case _:
            return ModelSettings(max_tokens=128_000)


def model_id_from_spec(spec: str) -> str:
    """Extract the model ID, preserving slashes used by hosted model names."""
    parts = spec.split("/")
    if len(parts) < 2:
        return spec
    provider = parts[0]
    if provider in {"claude-sdk", "codex"}:
        return parts[1]
    return "/".join(parts[1:])


def provider_from_spec(spec: str) -> str:
    """Extract the provider from a spec."""
    return spec.split("/", 1)[0]


def effort_from_spec(spec: str) -> Literal["low", "medium", "high", "xhigh", "max"] | None:
    """Extract effort level from a spec like 'claude-sdk/claude-opus-4-6/max'."""
    parts = spec.split("/")
    if len(parts) >= 3:
        effort = parts[2]
        if effort == "low":
            return "low"
        if effort == "medium":
            return "medium"
        if effort == "high":
            return "high"
        if effort == "xhigh":
            return "xhigh"
        if effort == "max":
            return "max"
    return None


def supports_vision(spec: str) -> bool:
    """Check if a model spec supports vision."""
    return model_id_from_spec(spec) in VISION_MODELS


def context_window(spec: str) -> int:
    """Get context window size for a model spec."""
    return CONTEXT_WINDOWS.get(model_id_from_spec(spec), 200_000)
