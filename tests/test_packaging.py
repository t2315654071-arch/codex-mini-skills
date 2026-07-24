from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "packaging" / "build_release.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("lite_release_builder", BUILD_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_package(tmp_path: Path) -> None:
    builder = load_builder()
    result = builder.build_release(REPO_ROOT, tmp_path)
    archive = Path(result["archive"])
    version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    root = f"codex-mini-skills-{version}"
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == result["sha256"]
    with ZipFile(archive) as package:
        names = package.namelist()
        assert {PurePosixPath(name).parts[0] for name in names} == {root}
        assert f"{root}/manifest.json" in names
        assert f"{root}/skills/document-extractor-lite/SKILL.md" in names
        assert f"{root}/examples/output/提取结果.csv" in names
        manifest = json.loads(package.read(f"{root}/manifest.json"))
        assert manifest["version"] == version
        assert manifest["file_count"] == len(manifest["files"])
        for entry in manifest["files"]:
            data = package.read(f"{root}/{entry['path']}")
            assert len(data) == entry["size_bytes"]
            assert hashlib.sha256(data).hexdigest() == entry["sha256"]
