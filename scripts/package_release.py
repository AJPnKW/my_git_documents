from __future__ import annotations

import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "reports" / "packages"
PACKAGE_RUNS = ROOT / "reports" / "data" / "package_runs"
MAX_PACKAGE_BYTES = 10_000 * 1024
EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    "backups",
    "cache",
    "reports",
    "temp",
    "web",
}
EXCLUDED_NAMES = {
    "auth_config.local.json",
    "local_project_summary.html",
}


class PackageSizeExceededError(RuntimeError):
    pass


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    return path.is_file()


def iter_package_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if should_include(path))


def build_archive(temp_target: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(temp_target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT))
            if temp_target.exists() and temp_target.stat().st_size > MAX_PACKAGE_BYTES:
                raise PackageSizeExceededError(
                    f"package exceeded max size of {MAX_PACKAGE_BYTES} bytes while adding {path}"
                )


def build_manifest(stamp: str, status: str, files: list[Path], archive_bytes: int, target: Path, error: str | None = None) -> dict:
    source_bytes = sum(path.stat().st_size for path in files)
    return {
        "stamp": stamp,
        "status": status,
        "package_path": str(target.relative_to(ROOT)).replace("\\", "/"),
        "package_bytes": archive_bytes,
        "package_kb": round(archive_bytes / 1024, 2),
        "max_package_bytes": MAX_PACKAGE_BYTES,
        "max_package_kb": round(MAX_PACKAGE_BYTES / 1024, 2),
        "source_file_count": len(files),
        "source_bytes": source_bytes,
        "source_kb": round(source_bytes / 1024, 2),
        "package_purpose": "Create a bounded release package of repo source assets only.",
        "excluded_parts": sorted(EXCLUDED_PARTS),
        "excluded_names": sorted(EXCLUDED_NAMES),
        "error": error,
        "files": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
            }
            for path in files
        ],
    }


def write_manifest(stamp: str, manifest: dict) -> Path:
    PACKAGE_RUNS.mkdir(parents=True, exist_ok=True)
    manifest_path = PACKAGE_RUNS / f"my_git_documents__package_run__{stamp}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d__%H%M%S")
    target = PACKAGES / f"my_git_documents__package__{stamp}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)

    files = iter_package_files()
    fd, temp_name = tempfile.mkstemp(prefix="my_git_documents__", suffix=".zip")
    os.close(fd)
    temp_target = Path(temp_name)

    try:
        build_archive(temp_target, files)
        final_size = temp_target.stat().st_size
        if final_size > MAX_PACKAGE_BYTES:
            raise PackageSizeExceededError(
                f"package exceeded max size of {MAX_PACKAGE_BYTES} bytes: {final_size} bytes"
            )
        shutil.move(str(temp_target), str(target))
        manifest_path = write_manifest(
            stamp,
            build_manifest(stamp, "success", files, final_size, target),
        )
    except Exception as exc:
        archive_bytes = temp_target.stat().st_size if temp_target.exists() else 0
        manifest_path = write_manifest(
            stamp,
            build_manifest(
                stamp,
                "failed",
                files,
                archive_bytes,
                target,
                error=str(exc),
            ),
        )
        if temp_target.exists():
            temp_target.unlink()
        raise

    print(target)
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
