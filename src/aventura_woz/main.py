"""Punto de entrada de WOZ.exe (desktop + navegador vía pygbag)."""

from __future__ import annotations

import asyncio
import sys
import traceback

import pygame

from aventura_woz import config


def _is_web() -> bool:
    return sys.platform in ("emscripten", "wasi")


async def main(screen: pygame.Surface | None = None) -> None:
    try:
        await _run_game(screen)
    except Exception:
        traceback.print_exc()
        if _is_web():
            while True:
                await asyncio.sleep(1)
        raise


async def _run_game(screen: pygame.Surface | None = None) -> None:
    # Import diferido: evita trabajo pesado antes del primer frame web
    from aventura_woz.game import Game

    if not pygame.get_init():
        pygame.init()
    pygame.display.set_caption(
        "WOZ.exe — Leonardo Bianco · inspirado en Flavio Speche"
    )

    if screen is None:
        if _is_web():
            screen = pygame.display.set_mode((1280, 800))
        else:
            screen = pygame.display.set_mode(
                (config.WINDOW_WIDTH, config.WINDOW_HEIGHT),
                pygame.RESIZABLE,
            )

    clock = pygame.time.Clock()
    screen.fill((0, 0, 40))
    pygame.display.flip()
    await asyncio.sleep(0)

    game = Game()
    print("WOZ.exe: game ready", flush=True)

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
        await asyncio.sleep(0)

    game.music.stop()
    if not _is_web():
        pygame.quit()
        sys.exit(0)


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
