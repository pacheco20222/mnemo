from mnemo.embeddings import embed_text


def test_embed_text_returns_768_floats():
    vector = embed_text("hello world")
    assert len(vector) == 768
    assert all(isinstance(v, float) for v in vector)


def test_embed_text_differs_for_different_input():
    a = embed_text("the qdrant collection stores vectors")
    b = embed_text("the weather today is sunny and warm")
    assert a != b
