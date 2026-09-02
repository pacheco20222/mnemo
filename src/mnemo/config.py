import os

QDRANT_URL = os.environ.get("MNEMO_QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.environ.get("MNEMO_OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
VECTOR_SIZE = 768
COLLECTION_NAME = os.environ.get("MNEMO_COLLECTION", "memories")
VALID_TYPES = frozenset({"decision", "architecture", "bug", "todo", "note", "checkpoint"})


def get_project() -> str:
    project = os.environ.get("MNEMO_PROJECT", "").strip()
    if not project:
        raise RuntimeError(
            "MNEMO_PROJECT is not set. Each repo's .mcp.json must set it so "
            "memories are scoped to the right project."
        )
    return project


def validate_type(type_: str) -> None:
    if type_ not in VALID_TYPES:
        raise ValueError(f"invalid type {type_!r}, must be one of {sorted(VALID_TYPES)}")
