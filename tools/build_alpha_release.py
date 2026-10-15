"""Build a deterministic, source-only Alpha release kit from a sanitized export."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


FORBIDDEN_SUFFIXES = {
    ".7z", ".a", ".bin", ".bios", ".dll", ".elf", ".exe", ".gif", ".irx",
    ".iso", ".jpg", ".jpeg", ".lib", ".o", ".obj", ".png", ".ps2", ".rar",
    ".rom", ".sav", ".spv", ".webp", ".zip",
}
FORBIDDEN_PREFIXES = ("extracted/", "mc0/", "mc1/", "output/", "src/recomp/generated/", "src/recomp/chunks/")
FIXED_ZIP_TIME = (2026, 10, 15, 0, 0, 0)


def _collect(root: Path) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    if not root.is_dir():
        raise ValueError(f"release input is not a directory: {root}")
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"forbidden release payload: symlink {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        lower = relative.lower()
        if Path(lower).suffix in FORBIDDEN_SUFFIXES or lower.startswith(FORBIDDEN_PREFIXES):
            raise ValueError(f"forbidden release payload: {relative}")
        data = path.read_bytes()
        if b"\0" in data or data.startswith((b"MZ", b"\x7fELF")):
            raise ValueError(f"forbidden release payload: binary content in {relative}")
        payloads[relative] = data
    return payloads


def build_source_kit(publication_dir: Path, launcher_dir: Path, output: Path, version: str) -> dict:
    publication_dir = Path(publication_dir)
    launcher_dir = Path(launcher_dir)
    output = Path(output)
    payloads = _collect(publication_dir)
    for name, data in _collect(launcher_dir).items():
        if name in payloads:
            raise ValueError(f"duplicate release payload: {name}")
        payloads[name] = data

    prefix = f"Noble-Archimedes-{version}"
    manifest = {
        "format": 1,
        "version": version,
        "binary_included": False,
        "game_content_included": False,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payloads.items())},
    }
    payloads["RELEASE_MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payloads.items()):
            info = zipfile.ZipInfo(f"{prefix}/{name}", FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication-dir", type=Path, required=True)
    parser.add_argument("--launcher-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", default="0.1.0-alpha")
    args = parser.parse_args()
    manifest = build_source_kit(args.publication_dir, args.launcher_dir, args.output, args.version)
    print(json.dumps({"output": str(args.output.resolve()), "files": len(manifest["files"]), "version": args.version}))


if __name__ == "__main__":
    main()
