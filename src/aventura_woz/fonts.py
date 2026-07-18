"""Fuentes: TTF embebida (definición nítida; mismo tamaño visual que antes)."""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from aventura_woz import config

_ASSETS = Path(__file__).resolve().parent / "assets"
_TTF = _ASSETS / "DejaVuSansMono.ttf"
_TTF_BOLD = _ASSETS / "DejaVuSansMono-Bold.ttf"

_cache: dict[tuple[int, bool], pygame.font.Font] = {}


def _is_web() -> bool:
    return sys.platform in ("emscripten", "wasi")


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Fuente usable; TTF del proyecto sin agrandar (evita solapes en UI)."""
    # DejaVu a N px rinde más alto que SysFont/None: compensar ~1–2 px
    ttf_size = max(8, size - 1)
    key = (ttf_size, bold)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    path = _TTF_BOLD if bold and _TTF_BOLD.exists() else _TTF
    font: pygame.font.Font | None = None
    last_err: Exception | None = None

    if path.exists():
        try:
            font = pygame.font.Font(str(path), ttf_size)
            if bold and path == _TTF:
                font.set_bold(True)
        except (pygame.error, OSError) as exc:
            last_err = exc
            font = None

    if font is None:
        names: list[str | None]
        if _is_web():
            names = ["dejavusansmono", "freesans", None]
        else:
            names = [config.FONT_FAMILY, "consolas", None]
        for name in names:
            try:
                if name is None:
                    font = pygame.font.Font(None, size)
                else:
                    font = pygame.font.SysFont(name, size, bold=bold)
                font.render("A", True, (255, 255, 255))
                break
            except (pygame.error, OSError, TypeError, ValueError) as exc:
                last_err = exc
                font = None

    if font is None:
        raise RuntimeError(f"No se pudo crear fuente ({last_err})")

    _cache[key] = font
    return font
