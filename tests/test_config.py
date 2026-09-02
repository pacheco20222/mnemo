import pytest

from mnemo import config


def test_get_project_reads_env(monkeypatch):
    monkeypatch.setenv("MNEMO_PROJECT", "villenca")
    assert config.get_project() == "villenca"


def test_get_project_raises_when_unset(monkeypatch):
    monkeypatch.delenv("MNEMO_PROJECT", raising=False)
    with pytest.raises(RuntimeError):
        config.get_project()


def test_get_project_raises_when_blank(monkeypatch):
    monkeypatch.setenv("MNEMO_PROJECT", "   ")
    with pytest.raises(RuntimeError):
        config.get_project()


def test_validate_type_accepts_known_types():
    for known in ("decision", "architecture", "bug", "todo", "note", "checkpoint"):
        config.validate_type(known)  # must not raise


def test_validate_type_rejects_unknown():
    with pytest.raises(ValueError):
        config.validate_type("nonsense")
