import httpx

from mnemo import config


def embed_text(text: str) -> list[float]:
    response = httpx.post(
        f"{config.OLLAMA_URL}/api/embeddings",
        json={"model": config.EMBED_MODEL, "prompt": text},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["embedding"]
