import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="mnemo setup")
    parser.add_argument("--project", default=None)
    args = parser.parse_args(argv)

    install_dir = Path(__file__).resolve().parents[2]
    project = args.project or "your-project-name"

    if sys.platform == "win32":
        install_path = install_dir.as_posix()
        mcp_json = json.dumps(
            {
                "mcpServers": {
                    "mnemo": {
                        "command": "uv",
                        "args": ["--directory", install_path, "run", "mnemo"],
                        "env": {"MNEMO_PROJECT": project},
                    }
                }
            },
            indent=2,
        )
        escaped_project = project.replace("'", "''")
        hook_command = (
            'powershell.exe -NoProfile -Command '
            f'"$env:MNEMO_PROJECT=\'{escaped_project}\'; '
            f"uv run --directory '{install_path}' mnemo-recall\""
        )
        hook_json = json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "startup|resume|clear",
                            "hooks": [{"type": "command", "command": hook_command}],
                        }
                    ]
                }
            },
            indent=2,
        )
        codex_cmd = (
            f'codex mcp add mnemo --env "MNEMO_PROJECT={project}" -- '
            f'uv run --directory "{install_path}" mnemo'
        )
    else:
        mcp_json = f"""{{
  "mcpServers": {{
    "mnemo": {{
      "command": "uv",
      "args": ["--directory", "{install_dir}", "run", "mnemo"],
      "env": {{
        "MNEMO_PROJECT": "{project}"
      }}
    }}
  }}
}}"""

        hook_json = f"""{{
  "hooks": {{
    "SessionStart": [
      {{
        "matcher": "startup|resume|clear",
        "hooks": [
          {{
            "type": "command",
            "command": "MNEMO_PROJECT={project} uv run --directory {install_dir} mnemo-recall"
          }}
        ]
      }}
    ]
  }}
}}"""

        codex_cmd = f"codex mcp add mnemo --env MNEMO_PROJECT={project} -- uv run --directory {install_dir} mnemo"

    print("Add this to your repo's .mcp.json (Claude Code):\n")
    print(mcp_json)
    print("\nOptional — add this to your repo's .claude/settings.json to auto-load checkpoints and documents every session:\n")
    print(hook_json)
    print("\nFor Codex, run:\n")
    print(codex_cmd)
    if args.project is None:
        print("\n(Replace 'your-project-name' with your actual project id, or re-run with --project NAME.)")
