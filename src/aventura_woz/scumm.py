"""Sistema point-and-click estilo SCUMM / Maniac Mansion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame

from aventura_woz import config
from aventura_woz.state import GameState


ActionFn = Callable[[GameState], None]


@dataclass
class Hotspot:
    """Zona clickeable en la escena."""

    name: str
    rect: pygame.Rect
    # verbo -> acción
    actions: dict[str, ActionFn] = field(default_factory=dict)
    # si True, Walk to ejecuta la primera acción de viaje
    is_exit: bool = False


@dataclass
class VerbHit:
    verb: str
    rect: pygame.Rect


def verb_grid_rects(use_scumm: bool = True) -> list[VerbHit]:
    """Verbos anclados justo arriba del status (sin hueco negro)."""
    hits: list[VerbHit] = []
    cell_w, cell_h = 98, 16
    panel_bottom = config.LOGICAL_H - config.STATUS_H
    start_y = panel_bottom - config.VERB_ROWS_H
    start_x = 6
    for i, verb in enumerate(config.VERBS):
        col = i % config.VERB_COLS
        row = i // config.VERB_COLS
        r = pygame.Rect(
            start_x + col * cell_w, start_y + row * cell_h, cell_w - 4, cell_h - 2
        )
        hits.append(VerbHit(verb, r))
    return hits


def inventory_rects(
    items: list[str], use_scumm: bool = True
) -> list[tuple[str, pygame.Rect]]:
    """Inventario a la derecha (no solapa con Volver)."""
    hits: list[tuple[str, pygame.Rect]] = []
    panel_bottom = config.LOGICAL_H - config.STATUS_H
    y0 = panel_bottom - config.VERB_ROWS_H
    x0 = 520
    # Máx. 2 ítems: caben entre título (y0) y status sin pisar Volver
    for i, item in enumerate(items[:2]):
        r = pygame.Rect(x0, y0 + 14 + i * 14, 112, 13)
        hits.append((item, r))
    return hits


def back_button_rect() -> pygame.Rect:
    """Volver entre verbos e inventario (sin solapar ítems)."""
    panel_bottom = config.LOGICAL_H - config.STATUS_H
    return pygame.Rect(400, panel_bottom - 16, 100, 14)


def build_sentence(verb: str, obj: str | None = None, prep: str = "", obj2: str | None = None) -> str:
    parts = [verb]
    if obj:
        parts.append(obj)
    if prep and obj2:
        parts.append(prep)
        parts.append(obj2)
    return " ".join(parts)


def default_response(verb: str, obj: str) -> str:
    templates = {
        "Ir a": f"No podés ir hacia {obj}. No sos un cursor mágico… o sí, pero no.",
        "Mirar": f"Es {obj}. Interesante. Tipo ‘interesante’ de documental de Discovery.",
        "Agarrar": f"No podés llevarte {obj}. Inventario ≠ agujero negro.",
        "Hablar": f"{obj} no responde. Awkward silence, modo Twin Peaks.",
        "Usar": f"No sabés cómo usar {obj}. Y eso que viste Terminator dos veces.",
        "Abrir": f"{obj} no se abre. Trancado con el candado de los 80: feo pero efectivo.",
        "Cerrar": f"{obj} no se cierra. Ya estaba cerrado. Plot twist.",
        "Empujar": f"Empujás {obj}. Nada. Como empujar un auto en una bajada… sin auto.",
        "Tirar": f"Tirás de {obj}. Nada. El universo se burla en 8-bit.",
        "Dar": f"No hay a quién darle {obj}. Qué generoso, igual.",
    }
    return templates.get(verb, f"No podés hacer eso con {obj}. El motor SCUMM se ofende.")
