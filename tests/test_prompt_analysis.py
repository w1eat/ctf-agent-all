from backend.prompts import ChallengeMeta, build_prompt


def test_binary_with_broker_prefers_ida_and_correct_file_id():
    meta = ChallengeMeta(name="pwn", category="pwn", connection_info="nc example.test 31337",
                         challenge_mode="attachment")
    prompt = build_prompt(meta, ["binary"], has_analysis_tools=True)
    assert "list_analysis_tools" in prompt
    assert "tool_name=survey_binary" in prompt
    assert "file_id" in prompt
    assert "FIRST ACTION REQUIRED" not in prompt
    assert prompt.index("IDA MCP first") < prompt.index("Inspect the attached binary")


def test_without_broker_preserves_shell_and_remote_priority():
    meta = ChallengeMeta(name="pwn", category="pwn", connection_info="nc example.test 31337")
    prompt = build_prompt(meta, ["binary"], has_analysis_tools=False, has_ghidra=True)
    assert "FIRST ACTION REQUIRED" in prompt
    assert "pyghidra" in prompt
    assert "list_analysis_tools" not in prompt


def test_unverified_ghidra_is_not_advertised():
    meta = ChallengeMeta(name="reverse", category="reverse")
    prompt = build_prompt(meta, ["binary"], container_arch="x86_64", has_ghidra=False)
    assert "pyghidra.open_program" not in prompt
    assert "Ghidra was not verified" in prompt
    assert "**Arch**    : x86_64" in prompt


def test_broker_without_attachment_does_not_demand_ida():
    meta = ChallengeMeta(name="remote", category="pwn", connection_info="nc example.test 31337")
    prompt = build_prompt(meta, [], has_analysis_tools=True)
    assert "FIRST ACTION REQUIRED" in prompt
    assert "survey_binary" not in prompt
