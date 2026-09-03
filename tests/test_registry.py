from pathlib import Path

import pytest

from mnemo import registry


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    path = tmp_path / "projects.json"
    monkeypatch.setenv("MNEMO_REGISTRY_PATH", str(path))
    return path


def test_lookup_returns_none_when_file_missing(isolated_registry):
    assert registry.lookup(Path("/some/never/registered/folder")) is None


def test_register_then_lookup_returns_project(isolated_registry):
    folder = Path("/Users/test/myrepo")
    registry.register(folder, "myproject")
    assert registry.lookup(folder) == "myproject"


def test_register_creates_parent_directory(tmp_path, monkeypatch):
    nested = tmp_path / "nested" / "dir" / "projects.json"
    monkeypatch.setenv("MNEMO_REGISTRY_PATH", str(nested))
    registry.register(Path("/a/b"), "proj")
    assert nested.exists()


def test_reregistering_same_path_overwrites(isolated_registry):
    folder = Path("/Users/test/myrepo")
    registry.register(folder, "first-name")
    registry.register(folder, "second-name")
    assert registry.lookup(folder) == "second-name"


def test_two_different_paths_coexist(isolated_registry):
    folder_a = Path("/Users/test/repo-a")
    folder_b = Path("/Users/test/repo-b")
    registry.register(folder_a, "project-a")
    registry.register(folder_b, "project-b")
    assert registry.lookup(folder_a) == "project-a"
    assert registry.lookup(folder_b) == "project-b"


def test_lookup_uses_resolved_absolute_path(isolated_registry, tmp_path):
    real_dir = tmp_path / "realdir"
    real_dir.mkdir()
    registry.register(real_dir, "resolved-project")
    assert registry.lookup(Path(str(real_dir) + "/.")) == "resolved-project"
