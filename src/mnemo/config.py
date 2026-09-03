import os
from pathlib import Path

from mnemo import registry

QDRANT_URL = os.environ.get("MNEMO_QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.environ.get("MNEMO_OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
VECTOR_SIZE = 768
COLLECTION_NAME = os.environ.get("MNEMO_COLLECTION", "memories")
VALID_TYPES = frozenset({"decision", "architecture", "bug", "todo", "note", "checkpoint"})


def get_project() -> str:
    project = os.environ.get("MNEMO_PROJECT", "").strip()
    if project:
        return project
    try:
        registered = registry.lookup(Path.cwd())
    except registry.RegistryError as e:
        raise RuntimeError(
            f"MNEMO_PROJECT is not set, and the folder registry couldn't "
            f"be read: {e}. Fix or delete the file and re-register this "
            f"folder."
        ) from e
    if registered:
        return registered
    raise RuntimeError(
        "MNEMO_PROJECT is not set and this folder isn't registered. Ask "
        "Claude to register this folder as a project "
        "(memory_register_project), or run `mnemo register --project X` "
        "yourself."
    )


def validate_type(type_: str) -> None:
    if type_ not in VALID_TYPES:
        raise ValueError(f"invalid type {type_!r}, must be one of {sorted(VALID_TYPES)}")
