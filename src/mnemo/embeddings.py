from fastembed import TextEmbedding

from mnemo import config

_model = TextEmbedding(model_name=config.EMBED_MODEL)


def embed_text(text: str) -> list[float]:
    embedding = next(iter(_model.embed([text])))
    return embedding.tolist()
