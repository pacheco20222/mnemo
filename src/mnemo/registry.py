import json
import os
from pathlib import Path


def registry_path() -> Path:
    override = os.environ.get("MNEMO_REGISTRY_PATH", "").strip()
    if override:
        return Path(override)
    return Path.home() / ".mnemo" / "projects.json"


def _load(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def register(cwd: Path, project: str) -> None:
    path = registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _load(path)
    data[str(cwd.resolve())] = project
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def lookup(cwd: Path) -> str | None:
    data = _load(registry_path())
    return data.get(str(cwd.resolve()))
