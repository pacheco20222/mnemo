import os

from mnemo import config, recall, store


def test_latest_checkpoint_returns_none_when_nothing_saved():
    result = recall.latest_checkpoint("a-project-with-no-checkpoints-ever")
    assert result is None


def test_latest_checkpoint_formats_found_result():
    client = store.get_client()
    collection = os.environ["MNEMO_COLLECTION"]
    store.ensure_collection(client, collection)
    store.add_memory(
        client, [0.1] * 768, "investigated the auth bug, next step is X",
        "mnemo-test", "checkpoint", collection=collection,
    )

    result = recall.latest_checkpoint("mnemo-test")
    assert result is not None
    assert "investigated the auth bug, next step is X" in result


def test_latest_checkpoint_fails_open_on_connection_error(monkeypatch):
    monkeypatch.setattr(config, "QDRANT_URL", "http://localhost:1")
    result = recall.latest_checkpoint("mnemo-test")
    assert result is None


def test_overview_document_returns_none_when_nothing_saved():
    result = recall.overview_document("a-project-with-no-overview-ever")
    assert result is None


def test_overview_document_formats_found_result():
    client = store.get_client()
    collection = os.environ["MNEMO_COLLECTION"]
    store.ensure_collection(client, collection)
    store.set_document(
        client, [0.2] * 768, "this project does X", "mnemo-test", "mnemo-test", "architecture",
        collection=collection,
    )

    result = recall.overview_document("mnemo-test")
    assert result is not None
    assert "this project does X" in result


def test_overview_document_fails_open_on_connection_error(monkeypatch):
    monkeypatch.setattr(config, "QDRANT_URL", "http://localhost:1")
    result = recall.overview_document("mnemo-test")
    assert result is None
