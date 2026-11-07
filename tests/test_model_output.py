import pytest
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import FunctionModel

from backend.agents.solver import _output_type_for_model
from backend.model_output import CompleteJSONOutput, _complete_json_containers
from backend.output_types import FlagFound


@pytest.mark.parametrize(("raw", "expected"), [
    ('{"flag":"FLAG{x}"', '{"flag":"FLAG{x}"}'),
    ('{"a":[{"b":"braces } [ inside a string"}', '{"a":[{"b":"braces } [ inside a string"}]}'),
    ('{"a":"escaped \\" quote"', '{"a":"escaped \\" quote"}'),
])
def test_missing_closing_containers_preserve_existing_values(raw, expected):
    assert _complete_json_containers(raw) == expected


@pytest.mark.asyncio
async def test_prompted_union_recovers_missing_brace_without_another_model_call():
    calls = []
    raw = '{"result":{"kind":"FlagFound","data":{"flag":"FLAG{exact}","method":"derived"}}'

    def respond(messages, info):
        calls.append(messages)
        return ModelResponse(parts=[TextPart(raw)])

    agent = Agent(
        FunctionModel(respond), output_type=_output_type_for_model("deepseek/test"),
        capabilities=[CompleteJSONOutput()], retries={"output": 0},
    )
    result = await agent.run("Return the result")
    assert isinstance(result.output, FlagFound)
    assert result.output.flag == "FLAG{exact}"
    assert result.output.method == "derived"
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("raw", [
    '{"result":{"kind":"FlagFound","data":{"flag":"FLAG{unfinished',
    '{"result":{"kind":"FlagFound","data":{"flag":',
    '{"result":{"kind":"Unknown","data":{"flag":"FLAG{x}","method":"derived"}}',
    '{"result":{"kind":"FlagFound","data":{"flag":"FLAG{x}"}}',
    '{"result":{"kind":"FlagFound","data":{"flag":"FLAG{x}","method":"derived",}}',
])
async def test_recovery_never_fills_missing_values_or_bypasses_schema(raw):
    def respond(messages, info):
        return ModelResponse(parts=[TextPart(raw)])

    agent = Agent(
        FunctionModel(respond), output_type=_output_type_for_model("deepseek/test"),
        capabilities=[CompleteJSONOutput()], retries={"output": 0},
    )
    with pytest.raises(UnexpectedModelBehavior):
        await agent.run("Return the result")


@pytest.mark.asyncio
async def test_recovery_does_not_rewrite_tool_arguments():
    def respond(messages, info):
        return ModelResponse(parts=[ToolCallPart("final_result", '{"flag":"FLAG{x}","method":"derived"')])

    agent = Agent(FunctionModel(respond), output_type=FlagFound,
                  capabilities=[CompleteJSONOutput()], retries={"output": 0})
    with pytest.raises(UnexpectedModelBehavior):
        await agent.run("Return the result")
