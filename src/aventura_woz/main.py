"""Punto de entrada de WOZ.exe (desktop + navegador vía pygbag)."""

from __future__ import annotations

import asyncio
import sys

import pygame

from aventura_woz import config
from aventura_woz.game import Game


def _is_web() -> bool:
    return sys.platform in ("emscripten", "wasi")


async def main() -> None:
    pygame.init()
    pygame.display.set_caption(
        "WOZ.exe — Leonardo Bianco · inspirado en Flavio Speche"
    )

    flags = 0 if _is_web() else pygame.RESIZABLE
    screen = pygame.display.set_mode(
        (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), flags
    )
    clock = pygame.time.Clock()
    game = Game()

    while game.state.running:
        dt = clock.tick(config.FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game.state.running = False
            elif event.type == pygame.VIDEORESIZE and not _is_web():
                w = max(event.w, 640)
                h = max(event.h, 400)
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        game.handle_events(events)
        game.update(dt)
        w, h = screen.get_size()
        game.draw(screen, w, h)
        pygame.display.flip()
        # Obligatorio para pygbag / navegador (cede el frame)
        await asyncio.sleep(0)

    game.music.stop()
    pygame.quit()
    if not _is_web():
        sys.exit(0)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
