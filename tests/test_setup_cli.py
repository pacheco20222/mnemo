import json
import sys

import pytest

from mnemo import setup_cli


def _printed_json(out: str, heading_after: str) -> dict:
    start = out.index("{")
    end = out.index(heading_after)
    return json.loads(out[start:end].strip())


def test_setup_prints_mcp_json_and_codex_command(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out
    assert '"MNEMO_PROJECT": "myproj"' in out
    if sys.platform == "win32":
        assert 'codex mcp add mnemo --env "MNEMO_PROJECT=myproj"' in out
    else:
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
    if sys.platform == "win32":
        assert "$env:MNEMO_PROJECT='myproj'" in out
    else:
        assert "MNEMO_PROJECT=myproj uv run --directory" in out
    assert "mnemo-recall" in out


@pytest.mark.skipif(sys.platform != "win32", reason="Windows output regression")
def test_setup_prints_valid_json_with_portable_windows_path(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out

    config = _printed_json(out, "Optional")
    install_path = config["mcpServers"]["mnemo"]["args"][1]

    assert "\\" not in install_path


@pytest.mark.skipif(sys.platform != "win32", reason="Windows output regression")
def test_setup_prints_native_windows_hook_command(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out
    hook_start = out.index("{", out.index("Optional"))
    hook_end = out.index("\n\nFor Codex")
    hook = json.loads(out[hook_start:hook_end])

    command = hook["hooks"]["SessionStart"][0]["hooks"][0]["command"]
    assert command.startswith("powershell.exe -NoProfile -Command ")


@pytest.mark.skipif(sys.platform != "win32", reason="Windows output regression")
def test_setup_prints_codex_path_quoted_for_powershell_and_cmd(capsys):
    setup_cli.main(["--project", "myproj"])
    out = capsys.readouterr().out

    codex_command = out.split("For Codex, run:\n\n", maxsplit=1)[1]
    assert '--directory "' in codex_command
    assert '" mnemo' in codex_command
