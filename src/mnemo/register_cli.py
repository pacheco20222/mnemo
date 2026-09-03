import argparse
import sys
from pathlib import Path

from mnemo import registry


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="mnemo register")
    parser.add_argument("--project", required=True)
    args = parser.parse_args(argv)

    project = args.project.strip()
    if not project:
        print("Error: --project must not be empty.", file=sys.stderr)
        raise SystemExit(1)

    cwd = Path.cwd()
    registry.register(cwd, project)
    print(f"Registered {cwd.resolve()} as project '{project}'.")
