"""Fuentes compatibles con desktop y WebAssembly (pygbag)."""

from __future__ import annotations

import sys

import pygame

from aventura_woz import config

# En WASM no hay Consolas; SysFont con nombre inexistente puede fallar.
_WEB_CANDIDATES = (
    "dejavusansmono",
    "dejavu sans mono",
    "freesans",
    "liberation mono",
    "courier",
    None,
)


def _is_web() -> bool:
    return sys.platform in ("emscripten", "wasi")


def make_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Devuelve una fuente usable; nunca lanza por falta de familia."""
    names: list[str | None]
    if _is_web():
        names = list(_WEB_CANDIDATES)
    else:
        names = [config.FONT_FAMILY, "consolas", "courier new", None]

    last_err: Exception | None = None
    for name in names:
        try:
            if name is None:
                font = pygame.font.Font(None, size)
            else:
                font = pygame.font.SysFont(name, size, bold=bold)
            # Smoke: algunas builds WASM devuelven fuente rota
            font.render("A", True, (255, 255, 255))
            return font
        except (pygame.error, OSError, TypeError, ValueError) as exc:
            last_err = exc
            continue

    # Último recurso
    try:
        return pygame.font.Font(None, size)
    except pygame.error as exc:
        raise RuntimeError(f"No se pudo crear fuente ({last_err})") from exc
