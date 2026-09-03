import json
import os
from pathlib import Path


def registry_path() -> Path:
    override = os.environ.get("MNEMO_REGISTRY_PATH", "").strip()
    if override:
        return Path(override)
    return Path.home() / ".mnemo" / "projects.json"


class RegistryError(Exception):
    """Raised when the registry file exists but can't be parsed as JSON."""


def _load(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise RegistryError(f"{path} exists but isn't valid JSON: {e}") from e


def register(cwd: Path, project: str) -> None:
    path = registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _load(path)
    data[str(cwd.resolve())] = project
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def lookup(cwd: Path) -> str | None:
    data = _load(registry_path())
    return data.get(str(cwd.resolve()))
