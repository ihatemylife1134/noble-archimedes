#!/usr/bin/env python3
"""
Reject build artifacts, generated Unreal content, and game-derived files from
the repository.

Run from anywhere:
    python UE5_Source/Tools/check_clean_repo.py

The active project at C:\\Projects\\NobleArchimedes keeps its own Binaries,
Intermediate, Saved, and Content/*.uasset files. None of those belong in the
source repository.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# The startup map is a deliberate, reviewed seed asset. Everything else under
# Content is authored as text (CSV / Markdown / JSON) and generated in-editor.
ALLOWED_BINARY_PATHS = {
    Path("UE5_Source/Content/Maps/Chap_01_AbandonedCastle.umap"),
}

FORBIDDEN_DIR_NAMES = {
    "Binaries",
    "Intermediate",
    "Saved",
    "DerivedDataCache",
    ".vs",
}

FORBIDDEN_SUFFIXES = {
    # Unreal generated / cooked content
    ".uasset",
    ".uexp",
    ".ubulk",
    ".pak",
    ".ucas",
    ".utoc",
    ".umap",
    # Compiled binaries
    ".exe",
    ".dll",
    ".lib",
    ".obj",
    ".pdb",
    ".ilk",
    ".exp",
    # Copyrighted game / disc material
    ".iso",
    ".elf",
    ".irx",
    ".pss",
    ".rom",
    ".suprx",
    ".bin",
    # Captured media and archives
    ".dds",
    ".wav",
    ".mp3",
    ".ogg",
    ".mp4",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
    ".zip",
    ".7z",
    ".rar",
}

FORBIDDEN_PREFIXES = (
    "src/recomp/generated/",
    "src/recomp/chunks/",
)

MAX_TRACKED_BYTES = 25 * 1024 * 1024


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("git ls-files failed; run this from the repository")
    raw = result.stdout.decode("utf-8", errors="replace")
    return [Path(item) for item in raw.split("\0") if item]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for relative in tracked_files():
        posix = relative.as_posix()

        if posix in {path.as_posix() for path in ALLOWED_BINARY_PATHS}:
            continue

        if any(part in FORBIDDEN_DIR_NAMES for part in relative.parts):
            errors.append("tracked build directory: %s" % posix)
            continue

        if posix.startswith(FORBIDDEN_PREFIXES):
            errors.append("tracked game-derived source: %s" % posix)
            continue

        if relative.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("tracked forbidden file type: %s" % posix)
            continue

        absolute = ROOT / relative
        try:
            size = absolute.stat().st_size
        except OSError:
            warnings.append("tracked file is missing on disk: %s" % posix)
            continue
        if size > MAX_TRACKED_BYTES:
            errors.append("tracked file is larger than 25 MB: %s (%.1f MB)" % (
                posix, size / (1024 * 1024)))

    # Keep the working tree honest too: these directories are never source.
    for directory in (
        "UE5_Source/Binaries",
        "UE5_Source/Intermediate",
        "UE5_Source/Saved",
        "UE5_Source/DerivedDataCache",
        "UE5_Source/.vs",
    ):
        if (ROOT / directory).exists():
            errors.append("generated directory exists in repository: %s" % directory)

    if errors:
        print("Repository is not clean:")
        for message in errors:
            print("  ERROR: " + message)
        return 1

    if warnings:
        print("Warnings:")
        for message in warnings:
            print("  WARNING: " + message)

    print("PASSED: tracked files contain no build artifacts or disallowed content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
