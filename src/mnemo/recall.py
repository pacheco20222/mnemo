import os

from mnemo import config, store


def latest_checkpoint(project: str) -> str | None:
    try:
        client = store.get_client()
        record = store.get_latest(client, project, "checkpoint")
    except Exception:
        # Deliberately fail open: a down Qdrant must never block session
        # start. Unlike config.get_project(), this isn't a security
        # boundary, just a best-effort convenience lookup.
        return None
    if record is None:
        return None
    return f"[Mnemo] Resuming from last checkpoint ({record['created_at']}):\n{record['content']}"


def overview_document(project: str) -> str | None:
    try:
        client = store.get_client()
        record = store.get_document(client, project, project)
    except Exception:
        # Same fail-open rationale as latest_checkpoint.
        return None
    if record is None:
        return None
    return f"[Mnemo] Project overview (updated {record['updated_at']}):\n{record['content']}"


def main() -> None:
    project = os.environ.get("MNEMO_PROJECT", "").strip()
    if not project:
        return
    overview = overview_document(project)
    if overview:
        print(overview)
    checkpoint = latest_checkpoint(project)
    if checkpoint:
        print(checkpoint)


if __name__ == "__main__":
    main()
