from pathlib import Path

from fastembed import TextEmbedding

from mnemo import config

_model = TextEmbedding(
    model_name=config.EMBED_MODEL,
    cache_dir=str(Path.home() / ".mnemo" / "models"),
    lazy_load=True,
)


def embed_text(text: str) -> list[float]:
    embedding = next(iter(_model.embed([text])))
    return embedding.tolist()
