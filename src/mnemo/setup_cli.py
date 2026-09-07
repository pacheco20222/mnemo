import argparse
import json
import shlex
import sys
from pathlib import Path


def _powershell_quote(value: str, *, nested: bool = False) -> str:
    """Quote a PowerShell literal, optionally inside an outer double-quoted string."""
    if nested:
        value = value.replace("`", "``").replace("$", "`$").replace('"', '\\`"')
    return "'" + value.replace("'", "''") + "'"


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="mnemo setup")
    parser.add_argument("--project", default=None)
    args = parser.parse_args(argv)

    install_dir = Path(__file__).resolve().parents[2]
    project = args.project or "your-project-name"

    if sys.platform == "win32":
        install_path = install_dir.as_posix()
        hook_command = (
            'powershell.exe -NoProfile -Command '
            f'"`$env:MNEMO_PROJECT={_powershell_quote(project, nested=True)}; '
            f"uv run --directory {_powershell_quote(install_path, nested=True)} "
            'mnemo-recall"'
        )
        codex_cmd = (
            "codex mcp add mnemo --env "
            f"{_powershell_quote(f'MNEMO_PROJECT={project}')} -- "
            f"uv run --directory {_powershell_quote(install_path)} mnemo"
        )
    else:
        install_path = str(install_dir)
        hook_command = (
            f"MNEMO_PROJECT={shlex.quote(project)} "
            f"uv run --directory {shlex.quote(install_path)} mnemo-recall"
        )
        codex_cmd = (
            f"codex mcp add mnemo --env {shlex.quote(f'MNEMO_PROJECT={project}')} -- "
            f"uv run --directory {shlex.quote(install_path)} mnemo"
        )

    mcp_config = {
        "mcpServers": {
            "mnemo": {
                "command": "uv",
                "args": ["--directory", install_path, "run", "mnemo"],
                "env": {"MNEMO_PROJECT": project},
            }
        }
    }
    hook_config = {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup|resume|clear",
                    "hooks": [{"type": "command", "command": hook_command}],
                }
            ]
        }
    }
    mcp_json = json.dumps(mcp_config, indent=2)
    hook_json = json.dumps(hook_config, indent=2)

    print("Add this to your repo's .mcp.json (Claude Code):\n")
    print(mcp_json)
    print("\nOptional — add this to your repo's .claude/settings.json to auto-load checkpoints and documents every session:\n")
    print(hook_json)
    print("\nFor Codex, run:\n")
    print(codex_cmd)
    if args.project is None:
        print("\n(Replace 'your-project-name' with your actual project id, or re-run with --project NAME.)")
