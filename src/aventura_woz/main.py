"""Punto de entrada de WOZ.exe (desktop + navegador vía pygbag)."""

from __future__ import annotations

import asyncio
import sys
import traceback

import pygame

from aventura_woz import config
from aventura_woz.game import Game


def _is_web() -> bool:
    return sys.platform in ("emscripten", "wasi")


async def main() -> None:
    try:
        await _run_game()
    except Exception:
        traceback.print_exc()
        if _is_web():
            # Mantener vivo el runtime para que la consola muestre el error
            while True:
                await asyncio.sleep(1)
        raise


async def _run_game() -> None:
    pygame.init()
    pygame.display.set_caption(
        "WOZ.exe — Leonardo Bianco · inspirado en Flavio Speche"
    )

    if _is_web():
        # Alinear con el framebuffer del template pygbag (1280×720)
        flags = getattr(pygame, "SCALED", 0)
        size = (1280, 720)
    else:
        flags = pygame.RESIZABLE
        size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    screen = pygame.display.set_mode(size, flags)
    clock = pygame.time.Clock()

    # Primer frame visible antes de cargar salas/imágenes pesadas
    screen.fill((0, 0, 40))
    pygame.display.flip()
    await asyncio.sleep(0)

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
    if not _is_web():
        pygame.quit()
        sys.exit(0)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
