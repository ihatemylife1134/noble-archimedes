import importlib.util
import json
from pathlib import Path
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build_alpha_release.py"


def load_builder():
    assert SCRIPT.exists(), "Alpha release builder is missing"
    spec = importlib.util.spec_from_file_location("build_alpha_release", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_kit_is_deterministic_and_contains_launcher(tmp_path):
    builder = load_builder()
    publication = tmp_path / "publication"
    launchers = tmp_path / "launchers"
    publication.mkdir()
    launchers.mkdir()
    (publication / "README.md").write_text("public source\n", encoding="utf-8")
    (publication / "PUBLICATION_MANIFEST.json").write_text("{}\n", encoding="utf-8")
    (launchers / "Launch Native.cmd").write_text("@echo off\r\n", encoding="utf-8")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    first_manifest = builder.build_source_kit(publication, launchers, first, "0.1.0-alpha")
    second_manifest = builder.build_source_kit(publication, launchers, second, "0.1.0-alpha")

    assert first.read_bytes() == second.read_bytes()
    assert first_manifest == second_manifest
    with zipfile.ZipFile(first) as archive:
        names = set(archive.namelist())
        assert "Noble-Archimedes-0.1.0-alpha/README.md" in names
        assert "Noble-Archimedes-0.1.0-alpha/Launch Native.cmd" in names
        release_manifest = json.loads(
            archive.read("Noble-Archimedes-0.1.0-alpha/RELEASE_MANIFEST.json")
        )
        assert release_manifest["version"] == "0.1.0-alpha"
        assert release_manifest["binary_included"] is False


def test_source_kit_rejects_binary_payloads(tmp_path):
    builder = load_builder()
    publication = tmp_path / "publication"
    launchers = tmp_path / "launchers"
    publication.mkdir()
    launchers.mkdir()
    (publication / "NobleArchimedes.exe").write_bytes(b"MZ" + b"\0" * 30)

    with pytest.raises(ValueError, match="forbidden release payload"):
        builder.build_source_kit(publication, launchers, tmp_path / "release.zip", "0.1.0-alpha")
