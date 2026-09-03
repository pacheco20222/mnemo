import argparse
from pathlib import Path

from mnemo import registry


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="mnemo register")
    parser.add_argument("--project", required=True)
    args = parser.parse_args(argv)

    cwd = Path.cwd()
    registry.register(cwd, args.project)
    print(f"Registered {cwd.resolve()} as project '{args.project}'.")
