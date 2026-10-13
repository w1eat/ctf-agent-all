"""Pydantic Settings — credentials from .env file + environment variables."""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Generic OpenAI-compatible model endpoint. These take precedence when set.
    model_name: str = ""
    api_key: str = ""
    base_url: str = ""

    # Platform
    platform: str = "auto"
    platform_url: str = ""
    platform_login: bool = False
    browser_profile_dir: str = ".runtime/playwright-profile"
    browser_download_dir: str = ".runtime/downloads"
    platform_recipe_dir: str = ".runtime/recipes"
    challenge_state_db_path: str = ".runtime/challenge_state.sqlite3"
    challenge_run_id: str = ""
    run_log_stamp: str = ""
    attachment_download_timeout_seconds: int = 60
    attachment_max_retries: int = 3
    preparation_concurrency: int = 4
    coordinator_decision_timeout_seconds: int = 180  # 0 disables the timeout.
    coordinator_full_access: bool = False
    solver_attempt_timeout_seconds: int = 1800
    solver_max_tool_steps_per_attempt: int = 160
    solver_max_cost_usd: float = 15.0
    flag_verification_quorum: int = 2
    knowledge_db_path: str = ".runtime/knowledge.sqlite3"
    knowledge_enabled: bool = True
    external_knowledge_enabled: bool = True
    external_knowledge_dir: str = ".runtime/knowledge"
    external_knowledge_context_items: int = 4
    external_knowledge_context_chars: int = 4000
    writeup_model_spec: str = ""
    writeup_timeout_seconds: int = 180
    writeup_replay_timeout_seconds: int = 120
    challenge_types: list[str] = Field(default_factory=list)
    playwright_mcp_command: str = ""
    playwright_mcp_args: list[str] = Field(default_factory=list)
    playwright_browser: str = "chrome"
    playwright_executable_path: str = ""
    playwright_headless: bool = False
    solver_mcp_config: str = ""

    # CTFd
    ctfd_url: str = "http://localhost:8000"
    ctfd_user: str = "admin"
    ctfd_pass: str = "admin"
    ctfd_token: str = ""

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    deepseek_api_key: str = ""

    # Provider-specific (optional, for Bedrock/Azure/DeepSeek/Zen fallback)
    aws_region: str = "us-east-1"
    aws_bearer_token: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    opencode_zen_api_key: str = ""

    # Infra
    sandbox_image: str = "ctf-sandbox"
    max_concurrent_challenges: int = 10
    max_attempts_per_challenge: int = 5
    container_memory_limit: str = "16g"

    @field_validator(
        "max_concurrent_challenges",
        "max_attempts_per_challenge",
        "preparation_concurrency",
        "solver_attempt_timeout_seconds",
        "solver_max_tool_steps_per_attempt",
        "flag_verification_quorum",
        "writeup_timeout_seconds",
        "writeup_replay_timeout_seconds",
    )
    @classmethod
    def positive_limits(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("coordinator_decision_timeout_seconds")
    @classmethod
    def non_negative_coordinator_timeout(cls, value: int) -> int:
        if value < 0:
            raise ValueError("must be zero (disabled) or a positive integer")
        return value

    @field_validator("solver_max_cost_usd")
    @classmethod
    def non_negative_cost(cls, value: float) -> float:
        if value < 0:
            raise ValueError("must be non-negative")
        return value

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
