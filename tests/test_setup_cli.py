from mnemo import setup_cli


def test_setup_prints_mcp_json_and_codex_command(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out
    assert '"MNEMO_PROJECT": "myproj"' in out
    assert "codex mcp add mnemo --env MNEMO_PROJECT=myproj" in out
    assert '"command": "uv"' in out


def test_setup_uses_placeholder_when_no_project_given(capsys):
    setup_cli.main([])
    out = capsys.readouterr().out
    assert "your-project-name" in out


def test_setup_prints_session_start_hook_block(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out
    assert '"matcher": "startup|resume|clear"' in out
    assert "MNEMO_PROJECT=myproj uv run --directory" in out
    assert "mnemo-recall" in out
