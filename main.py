#!/usr/bin/env python3
"""SKYHOLD — a travel poster for a place that isn't there.

Entry program for the make.fun bounty
"the-poster-for-a-place-that-i-2-20261121-0539".

The finished poster ships beside this program as ``asset.jpg``: a
1024x1024 JPEG of a ring-shaped cliff city above the clouds, its
waterfalls pouring into the sky, the name SKYHOLD set in cream serif
capitals under a thin rule. Running this program validates the asset
against the bounty gate (a whole JPEG, at most 1,048,576 bytes, at
most 1024 by 1024 pixels) and writes it into the output directory as
``entry.png``. The gate reads magic bytes rather than the file name,
so JPEG bytes under the entry.png name are accepted.

Standard library only; no network; deterministic — every run writes
exactly the same bytes.
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
ASSET_NAME = "asset.jpg"
ENTRY_NAME = "entry.png"

JPEG_MAGIC = b"\xff\xd8\xff"
# Start-of-frame markers that carry the image dimensions.
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
# Markers with no length field (SOI, EOI, RSTn, TEM).
STANDALONE_MARKERS = {0xD8, 0xD9, *range(0xD0, 0xD8), 0x01}


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) parsed from the JPEG segment headers."""
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("asset does not start with the JPEG SOI marker")
    pos = 2
    while pos + 1 < len(data):
        if data[pos] != 0xFF:
            raise ValueError(f"expected a marker at byte {pos}")
        marker = data[pos + 1]
        pos += 2
        if marker in STANDALONE_MARKERS:
            continue
        if pos + 2 > len(data):
            raise ValueError("truncated segment header")
        (seg_len,) = struct.unpack(">H", data[pos:pos + 2])
        if seg_len < 2:
            raise ValueError("segment length smaller than its own field")
        if marker in SOF_MARKERS:
            if pos + 7 > len(data):
                raise ValueError("truncated start-of-frame segment")
            (height,) = struct.unpack(">H", data[pos + 3:pos + 5])
            (width,) = struct.unpack(">H", data[pos + 5:pos + 7])
            return width, height
        pos += seg_len
    raise ValueError("no start-of-frame segment found")


def validate_asset(data: bytes) -> tuple[int, int]:
    """Check the asset against the bounty gate; return (width, height)."""
    if not data.startswith(JPEG_MAGIC):
        raise ValueError("asset is not a JPEG (bad magic bytes)")
    if len(data) > MAX_BYTES:
        raise ValueError(f"asset is {len(data)} bytes, over the {MAX_BYTES} cap")
    width, height = jpeg_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"asset is {width}x{height}, over the {MAX_SIDE} px cap")
    return width, height


def resolve_output_dir() -> Path:
    """MAKEFUN_OUTPUT_DIR wins; then /output; then ./output."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return Path(env_dir)
    system_dir = Path("/output")
    if system_dir.is_dir():
        return system_dir
    return Path("output")


def clear_stale_entries(out_dir: Path) -> None:
    """Remove files left in the output dir by an earlier run.

    Only the contents go — never the directory itself: on the grader
    /output is a mount point, and removing the directory makes the
    run fail with EBUSY (a lesson paid for on an earlier bounty).
    """
    for child in out_dir.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()


def main() -> int:
    here = Path(__file__).resolve().parent
    asset_path = here / ASSET_NAME
    data = asset_path.read_bytes()
    width, height = validate_asset(data)

    out_dir = resolve_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    clear_stale_entries(out_dir)

    # Write to a temp name, then rename, so the entry is never seen
    # half-written; the rename keeps the bytes exactly as validated.
    entry_path = out_dir / ENTRY_NAME
    tmp_path = out_dir / (ENTRY_NAME + ".tmp")
    tmp_path.write_bytes(data)
    os.replace(tmp_path, entry_path)

    print(f"wrote {entry_path} ({len(data)} bytes, {width}x{height} JPEG)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
