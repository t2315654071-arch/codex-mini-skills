from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

from docx import Document


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR_PATH = (
    REPO_ROOT
    / "skills"
    / "document-extractor-lite"
    / "scripts"
    / "extract_lite.py"
)


def load_extractor():
    spec = importlib.util.spec_from_file_location("extract_lite_test", EXTRACTOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_docx(path: Path, text: str) -> None:
    document = Document()
    document.add_paragraph(text)
    document.save(path)


def test_docx_to_utf8_csv(tmp_path: Path) -> None:
    extractor = load_extractor()
    input_dir = tmp_path / "输入"
    input_dir.mkdir()
    create_docx(input_dir / "中文 文档.docx", "标题：合成测试 日期：2026-07-24")
    output = tmp_path / "输出" / "提取结果.csv"

    result = extractor.extract_directory(input_dir, output)

    assert result["processed"] == 1
    assert result["success"] == 1
    assert output.read_bytes().startswith(b"\xef\xbb\xbf")
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["文件名"] == "中文 文档.docx"
    assert rows[0]["状态"] == "成功"


def test_limit_is_enforced_without_partial_output(tmp_path: Path) -> None:
    extractor = load_extractor()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    for index in range(11):
        create_docx(input_dir / f"{index:02d}.docx", f"synthetic {index}")
    output = tmp_path / "result.csv"

    try:
        extractor.extract_directory(input_dir, output)
    except ValueError as exc:
        assert "最多处理10个文件" in str(exc)
    else:
        raise AssertionError("expected the free-tier limit to fail")
    assert not output.exists()


def test_unsupported_files_are_not_processed(tmp_path: Path) -> None:
    extractor = load_extractor()
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "image.png").write_bytes(b"synthetic")

    try:
        extractor.extract_directory(input_dir, tmp_path / "result.csv")
    except ValueError as exc:
        assert "没有受支持" in str(exc)
    else:
        raise AssertionError("expected unsupported-only input to fail")
