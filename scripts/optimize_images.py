#!/usr/bin/env python3
"""Create WebP variants of portrait PNGs in css/ (quality 82)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "css"
PARTNERS = ROOT / "assets" / "partners"

PAIRS = [
    ("portrait.png", "portrait.webp"),
    ("portrait_about_section.png", "portrait_about_section.webp"),
]

PARTNER_PAIRS = [
    ("aquamarine-logo.png", "aquamarine-logo.webp"),
    ("english please logo.png", "english please logo.webp"),
    ("select transfer logo.png", "select transfer logo.webp"),
    ("crigo group logo.png", "crigo group logo.webp"),
]


def convert_png_to_webp(png_name: str, webp_name: str) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow required: pip install Pillow") from exc

    src = CSS / png_name
    dst = CSS / webp_name
    if not src.exists():
        print(f"Skip {png_name} (not found)")
        return
    with Image.open(src) as img:
        img.save(dst, "WEBP", quality=82)
    print(f"Created {webp_name}")


def convert_partner_png_to_webp(png_name: str, webp_name: str) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow required: pip install Pillow") from exc

    src = PARTNERS / png_name
    dst = PARTNERS / webp_name
    if not src.exists():
        print(f"Skip partners/{png_name} (not found)")
        return
    with Image.open(src) as img:
        img.save(dst, "WEBP", quality=82)
    print(f"Created partners/{webp_name}")


def main() -> None:
    for png, webp in PAIRS:
        convert_png_to_webp(png, webp)
    for png, webp in PARTNER_PAIRS:
        convert_partner_png_to_webp(png, webp)


if __name__ == "__main__":
    main()
