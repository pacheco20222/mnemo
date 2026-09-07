import subprocess
import sys

import pytest

from mnemo.embeddings import embed_text


@pytest.mark.skipif(sys.platform != "win32", reason="Windows startup regression")
def test_import_defers_fastembed_on_windows():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import mnemo.embeddings; print('fastembed' in sys.modules)",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "False"


def test_embed_text_returns_768_floats():
    vector = embed_text("hello world")
    assert len(vector) == 768
    assert all(isinstance(v, float) for v in vector)


def test_embed_text_differs_for_different_input():
    a = embed_text("the qdrant collection stores vectors")
    b = embed_text("the weather today is sunny and warm")
    assert a != b
