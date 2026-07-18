"""Helpers de dibujo (scanlines, rects) para el renderer."""

from __future__ import annotations

import pygame

from aventura_woz import config

Color = tuple[int, int, int]


def fill(surface: pygame.Surface, color: Color = config.BG) -> None:
    surface.fill(color)


def rect(
    surface: pygame.Surface,
    x: int,
    y: int,
    w: int,
    h: int,
    color: Color,
    width: int = 0,
) -> None:
    pygame.draw.rect(surface, color, (x, y, w, h), width)


def hline(
    surface: pygame.Surface, x: int, y: int, w: int, color: Color
) -> None:
    pygame.draw.line(surface, color, (x, y), (x + w - 1, y))


def draw_scanlines(surface: pygame.Surface, alpha: int = config.SCANLINE_ALPHA) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for y in range(0, surface.get_height(), 2):
        pygame.draw.line(
            overlay, (0, 0, 0, alpha), (0, y), (surface.get_width(), y)
        )
    surface.blit(overlay, (0, 0))
