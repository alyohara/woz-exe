"""Entrada para pygbag (carpeta `src/` = app web).

Desktop:
  cd src && python main.py
  cd src && python -m aventura_woz

Web (local):
  python -m pygbag --ume_block 0 --disable-sound-format-error src
"""

from __future__ import annotations

import asyncio
import sys
import traceback


async def _boot() -> None:
    print("WOZ.exe: boot start", flush=True)
    try:
        import pygame

        pygame.init()
        # Misma resolución que el template pygbag (evita canvas vacío)
        screen = pygame.display.set_mode((1280, 720))
        screen.fill((0, 40, 30))
        pygame.display.flip()
        await asyncio.sleep(0)
        print("WOZ.exe: display ok", flush=True)

        from aventura_woz.main import main as game_main

        await game_main(screen)
    except Exception:
        traceback.print_exc()
        if sys.platform in ("emscripten", "wasi"):
            while True:
                await asyncio.sleep(1)
        raise


asyncio.run(_boot())
