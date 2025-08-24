#!/usr/bin/env python3
"""
Pack the contents of the 'modpack' directory into a ZIP archive.

- The archive will contain the files inside the modpack directory (not the top-level 'modpack' folder).
- Existing output ZIP will be overwritten.
- The output filename will automatically have the version from the VERSION file appended
  (e.g., m1ndworld_modpack-1.2.3.zip) if VERSION exists and is non-empty.
- Usage:
    python pack_modpack.py [<modpack_dir>] [<output_zip>]
  Defaults:
    modpack_dir = 'modpack'
    output_zip  = 'm1ndworld_modpack.zip'
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path


def _append_version_to_name(base_name: str, repo_root: Path) -> str:
    """Append version from VERSION file to the base filename before the extension.

    If VERSION is missing or empty, returns the base name unchanged.
    """
    version_file = repo_root / "VERSION"
    version = ""
    try:
        version = version_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        version = ""

    if not version:
        return base_name

    # Sanitize version for filename safety
    safe_version = "".join(c if (c.isalnum() or c in (".", "-", "_")) else "-" for c in version)
    p = Path(base_name)
    # Ensure there is an extension; default to .zip if none
    ext = p.suffix if p.suffix else ".zip"
    stem = p.stem if p.stem else "archive"
    return f"{stem}-{safe_version}{ext}"


def zip_modpack(modpack_dir: str = "modpack", output_zip: str = "m1ndworld_modpack.zip") -> Path:
    repo_root = Path(__file__).resolve().parent
    src = (repo_root / modpack_dir).resolve()
    # Compute output name with VERSION appended if available
    output_with_version = _append_version_to_name(output_zip, repo_root)
    out_path = (repo_root / output_with_version).resolve()

    if not src.exists() or not src.is_dir():
        print(f"Error: Modpack directory not found: {src}", file=sys.stderr)
        sys.exit(1)

    # Create ZIP (overwrites if exists)
    count = 0
    with zipfile.ZipFile(out_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in src.rglob("*"):
            if file_path.is_file():
                # Store paths relative to the modpack directory to avoid nesting the top-level dir
                arcname = file_path.relative_to(src).as_posix()
                zf.write(file_path, arcname)
                count += 1

    print(f"Created '{out_path.name}' with {count} files from '{src.name}'.")
    return out_path


if __name__ == "__main__":
    modpack_dir = sys.argv[1] if len(sys.argv) > 1 else "modpack"
    output_zip = sys.argv[2] if len(sys.argv) > 2 else "m1ndworld_modpack.zip"
    zip_modpack(modpack_dir, output_zip)
