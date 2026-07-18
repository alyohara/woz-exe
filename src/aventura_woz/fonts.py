"""Fuentes: TTF embebida (legible en desktop y WASM/pygbag)."""

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


def _effective_size(size: int) -> int:
    """En web el canvas 640×400 se escala: tipografía un poco mayor = más nítida."""
    if _is_web():
        return max(size + 2, int(round(size * 1.25)))
    return size


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Fuente usable; prioriza TTF del proyecto (no el bitmap por defecto)."""
    size = _effective_size(size)
    key = (size, bold)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    path = _TTF_BOLD if bold and _TTF_BOLD.exists() else _TTF
    font: pygame.font.Font | None = None
    last_err: Exception | None = None

    if path.exists():
        try:
            font = pygame.font.Font(str(path), size)
            if bold and path == _TTF:
                font.set_bold(True)
        except (pygame.error, OSError) as exc:
            last_err = exc
            font = None

    if font is None:
        # Fallback SysFont / default
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
