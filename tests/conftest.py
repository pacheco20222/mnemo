import os

os.environ.setdefault("MNEMO_PROJECT", "mnemo-test")
os.environ.setdefault("MNEMO_COLLECTION", "memories_test")

from mnemo import store

_reset_client = store.get_client()
if _reset_client.collection_exists(os.environ["MNEMO_COLLECTION"]):
    _reset_client.delete_collection(os.environ["MNEMO_COLLECTION"])
