from types import SimpleNamespace

import pytest

from backend.platforms.browser_mcp import BrowserAutoPlatformAdapter
from backend.platforms.recipes import PlatformRecipe, RecipeStep


@pytest.mark.asyncio
@pytest.mark.parametrize(("value", "data", "expected"), [
    ("Ready", {}, {"text": "Ready"}),
    ("Ready", {"time": None}, {"text": "Ready"}),
    ("", {"text": "Ready"}, {"text": "Ready"}),
    ("", {"time": 0}, {"time": 0}),
    ("", {"time": 0.1}, {"time": 0.1}),
    ("Ready", {"time": 1}, {"text": "Ready", "time": 1}),
])
async def test_recipe_wait_sends_only_set_tool_arguments(value, data, expected):
    adapter = BrowserAutoPlatformAdapter.__new__(BrowserAutoPlatformAdapter)
    calls = []

    async def call(name, arguments):
        assert name == "browser_wait_for"
        assert all(value is not None for value in arguments.values())
        calls.append(arguments)
        return "Ready"

    adapter.browser = SimpleNamespace(call=call)
    recipe = PlatformRecipe(platform_origin="https://platform.test", steps=[
        RecipeStep(action="wait_for", value=value, data=data),
    ])
    await adapter._execute_recipe(recipe, challenge_id="demo", purpose="submit")
    assert calls == [expected]


@pytest.mark.asyncio
@pytest.mark.parametrize("data", [
    {}, {"time": None}, {"time": True}, {"time": -1}, {"time": "1"},
    {"time": float("nan")}, {"time": float("inf")}, {"text": ["Ready"]},
])
async def test_invalid_recipe_wait_fails_before_calling_browser(data):
    adapter = BrowserAutoPlatformAdapter.__new__(BrowserAutoPlatformAdapter)
    recipe = PlatformRecipe(platform_origin="https://platform.test", steps=[
        RecipeStep(action="wait_for", data=data),
    ])
    with pytest.raises(RuntimeError, match="Recipe wait_for"):
        await adapter._execute_recipe(recipe, challenge_id="demo", purpose="submit")
