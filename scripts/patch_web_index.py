"""Ajusta index.html de pygbag: sin consola, sin scroll, AR 16:10 (640×400×2)."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def patch(index: Path) -> None:
    text = index.read_text(encoding="utf-8")

    text = re.sub(r'gui_divider\s*:\s*\d+', "gui_divider : 0", text)
    text = re.sub(r'xtermjs\s*:\s*"[^"]*"', 'xtermjs : "0"', text)
    text = re.sub(r'fb_ar\s*:\s*[\d.]+', "fb_ar   :  1.6", text)
    text = re.sub(r'fb_width\s*:\s*"[^"]*"', 'fb_width : "1280"', text)
    text = re.sub(r'fb_height\s*:\s*"[^"]*"', 'fb_height : "800"', text)
    text = text.replace('height="720px"', 'height="800px"')
    text = text.replace("Screen  : 1280x720", "Screen  : 1280x800")

    # Tras el boot, el template fuerza gui_divider = 1; lo anulamos
    text = text.replace(
        "platform.window.config.gui_divider = 1",
        "platform.window.config.gui_divider = 0",
    )

    css_fix = """
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            width: 100%;
            height: 100%;
            background-color: #000 !important;
        }
        #crt, #terminal, .xterm, #html {
            display: none !important;
        }
"""
    if "overflow: hidden !important" not in text:
        text = text.replace("body {\n            font-family: arial;", css_fix + "\n        body {\n            font-family: arial;")

    index.write_text(text, encoding="utf-8")
    print(f"patched {index}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    index = root / "src" / "build" / "web" / "index.html"
    if len(sys.argv) > 1:
        index = Path(sys.argv[1])
    if not index.is_file():
        raise SystemExit(f"missing {index}")
    patch(index)


if __name__ == "__main__":
    main()
