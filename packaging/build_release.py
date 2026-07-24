from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

PACKAGE_ID = "codex-mini-skills"
SKILL_ID = "document-extractor-lite"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_tree_clean(source: Path, target: Path) -> None:
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if any(part in {"__pycache__", ".pytest_cache"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Release不允许符号链接: {path}")
        if path.is_dir():
            (target / relative).mkdir(parents=True, exist_ok=True)
        elif path.suffix.lower() not in {".pyc", ".pyo"}:
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)


def write_zip(source_root: Path, archive: Path) -> None:
    with ZipFile(archive, "w", ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source_root.parent).as_posix()
            info = ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, path.read_bytes())


def build_release(repo_root: Path, output_dir: Path) -> dict:
    repo_root = repo_root.resolve()
    version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    runtime_version = json.loads(
        (
            repo_root
            / "skills"
            / SKILL_ID
            / "assets"
            / "runtime-version.json"
        ).read_text(encoding="utf-8")
    )["version"]
    if version != runtime_version:
        raise ValueError("VERSION与技能运行版本不一致")
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"{PACKAGE_ID}-{version}"
    temp_parent = repo_root / ".tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="release-", dir=temp_parent) as temp:
        package_root = Path(temp) / package_name
        package_root.mkdir()
        for name in (
            "VERSION",
            "requirements.txt",
            "LICENSE.md",
            "README.md",
            "CHANGELOG.md",
            "SECURITY.md",
            "install.ps1",
            "uninstall.ps1",
        ):
            shutil.copy2(repo_root / name, package_root / name)
        copy_tree_clean(repo_root / "skills", package_root / "skills")
        copy_tree_clean(repo_root / "examples", package_root / "examples")

        files = []
        for path in sorted(package_root.rglob("*")):
            if path.is_file():
                files.append(
                    {
                        "path": path.relative_to(package_root).as_posix(),
                        "size_bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
        manifest = {
            "package_format": 1,
            "package_id": PACKAGE_ID,
            "skill_id": SKILL_ID,
            "version": version,
            "created_at": datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z"),
            "file_count": len(files),
            "files": files,
        }
        (package_root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        archive = output_dir / f"{package_name}.zip"
        write_zip(package_root, archive)
        archive_hash = sha256_file(archive)
        checksum = output_dir / f"{package_name}.zip.sha256"
        checksum.write_text(
            f"{archive_hash}  {archive.name}\n",
            encoding="ascii",
        )
    return {
        "status": "ok",
        "version": version,
        "archive": str(archive.resolve()),
        "sha256": archive_hash,
        "checksum_file": str(checksum.resolve()),
        "file_count": len(files) + 1,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="构建免费版Release ZIP。")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        print(
            json.dumps(
                build_release(
                    args.repo_root,
                    args.output_dir or args.repo_root / "dist",
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {"status": "error", "error": f"{type(exc).__name__}: {exc}"},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
