#!/usr/bin/env python3
"""Build the resident Chinese BFNT font from HarmonyOS Sans SC.

Reads data/localization/zh_cn.json, collects every non-ASCII character used by
the catalog (plus a small set of symbols used by ML's UI), rasterizes each glyph
into a 32x32 one-bit BFNT cell and writes data/fonts/zh_cn.bfn.

The source font is kept unmodified in data/fonts/source/.  Its license is in
doc/HarmonyOS-Sans-LICENSE.txt and must be shipped with the generated font.
"""
from pathlib import Path
import argparse
import json
import struct

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FONT = ROOT / "data/fonts/source/HarmonyOS_Sans_SC_Regular.ttf"
DEFAULT_OUT = ROOT / "data/fonts/zh_cn.bfn"
CELL = 32
GLYPH_NAME = b"ML HarmonyOS SC"

# Symbols that can appear in English fallback strings or generated UI text.
# CJK punctuation is already covered through the translated catalog.
EXTRA_SYMBOLS = (
    "×÷±°µ·•…—–"
    "“”‘’「」『』【】《》〈〉"
    "、。！？：；（）［］｛｝＋－＝％＃＠＆＊／＼｜～"
    "￥€£¥©®™§¶†‡‰′″"
    "←→↑↓↔⇐⇒"
    "≈≠≤≥∞√∑∏∫∆∇"
    "✓✔✗✘★☆●○◆◇■□▲△▼▽▶◀"
)


def needed_chars(catalog_path):
    """Return (required catalog chars, optional extra symbols)."""
    messages = json.loads(catalog_path.read_text("utf-8"))["messages"]
    required = set()
    for message in messages:
        for field in ("source", "translation"):
            required.update(ch for ch in message.get(field, "") if ord(ch) > 0x7f)
    optional = {ch for ch in EXTRA_SYMBOLS if ord(ch) > 0x7f}
    return required, optional


def render_glyph(font, char, threshold):
    """Return a 32x32 1-bit bitmap as 4 bytes per row, centered in the cell."""
    bbox = font.getbbox(char)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if width <= 0 or height <= 0:
        return None
    x = round((CELL - width) / 2) - bbox[0]
    y = round((CELL - height) / 2) - bbox[1]
    canvas = Image.new("L", (CELL, CELL), 0)
    ImageDraw.Draw(canvas).text((x, y), char, font=font, fill=255)
    rows = bytearray()
    for row in range(CELL):
        value = 0
        for col in range(CELL):
            if canvas.getpixel((col, row)) >= threshold:
                value |= 1 << (7 - (col % 8))
            if col % 8 == 7:
                rows.append(value)
                value = 0
    if not any(rows):
        return None
    return bytes(rows)


def build(font_path, out_path, threshold):
    font = ImageFont.truetype(str(font_path), CELL)
    required, optional = needed_chars(ROOT / "data/localization/zh_cn.json")
    glyphs = {}
    missing = []
    skipped = []
    for char in sorted(required | optional):
        packed = int.from_bytes(char.encode("utf-8"), "little")
        bitmap = render_glyph(font, char, threshold)
        if bitmap is None:
            (missing if char in required else skipped).append(char)
            continue
        glyphs[packed] = struct.pack("<5H", CELL, CELL, CELL, 0, 0) + bitmap
    if missing:
        raise SystemExit("font has no usable glyph for: " + " ".join(
            "%s(U+%04X)" % (c, ord(c)) for c in missing))
    if skipped:
        print("optional symbols not in HarmonyOS Sans SC: " + " ".join(
            "%s(U+%04X)" % (c, ord(c)) for c in skipped))

    codes = sorted(glyphs)
    offsets = []
    bitmap_data = bytearray()
    for code in codes:
        offsets.append(len(bitmap_data))
        bitmap_data.extend(glyphs[code])

    header = bytearray(36)
    struct.pack_into("<IHH", header, 0, 0x00544E46, 0, CELL)
    struct.pack_into("<III", header, 8, 36, len(codes) * 4, len(bitmap_data))
    header[20:20 + len(GLYPH_NAME)] = GLYPH_NAME
    out_path.write_bytes(
        bytes(header)
        + struct.pack("<%dI" % len(codes), *codes)
        + struct.pack("<%dI" % len(codes), *offsets)
        + bytes(bitmap_data)
    )
    print(json.dumps(dict(font=str(font_path), output=str(out_path),
                          glyphs=len(codes), bytes=len(out_path.read_bytes()),
                          threshold=threshold), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--threshold", type=int, default=110)
    args = parser.parse_args()
    build(args.font, args.output, args.threshold)
