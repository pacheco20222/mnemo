import sys
from pathlib import Path

from mnemo import config

if sys.platform == "win32":
    _model = None

    def embed_text(text: str) -> list[float]:
        global _model
        if _model is None:
            from fastembed import TextEmbedding

            _model = TextEmbedding(
                model_name=config.EMBED_MODEL,
                cache_dir=str(Path.home() / ".mnemo" / "models"),
                lazy_load=True,
            )
        embedding = next(iter(_model.embed([text])))
        return embedding.tolist()

else:
    from fastembed import TextEmbedding

    _model = TextEmbedding(
        model_name=config.EMBED_MODEL,
        cache_dir=str(Path.home() / ".mnemo" / "models"),
        lazy_load=True,
    )

    def embed_text(text: str) -> list[float]:
        embedding = next(iter(_model.embed([text])))
        return embedding.tolist()
