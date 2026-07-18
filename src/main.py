"""Entrada para pygbag (carpeta `src/` = app web).

Desktop:
  cd src && python main.py
  cd src && python -m aventura_woz

Web (local):
  python -m pygbag --ume_block 0 --width 1280 --height 800 --CONSOLE 0 src
"""

from __future__ import annotations

import asyncio
import sys
import traceback

# Framebuffer web = 2× resolución lógica (640×400) → sin franjas laterales
_WEB_W = 1280
_WEB_H = 800


def _configure_web_page() -> None:
    """Sin consola pygbag ni scroll de la página."""
    try:
        import platform

        body = platform.document.body
        body.style.overflow = "hidden"
        body.style.margin = "0"
        body.style.background = "#000"
        platform.document.documentElement.style.overflow = "hidden"
        if hasattr(platform.window, "config"):
            platform.window.config.gui_divider = 0
        for sel in ("#crt", "#terminal", ".xterm"):
            try:
                el = platform.document.querySelector(sel)
                if el:
                    el.style.display = "none"
            except Exception:
                pass
        try:
            platform.window.window_resize()
        except Exception:
            pass
    except Exception:
        pass


async def _boot() -> None:
    print("WOZ.exe: boot start", flush=True)
    try:
        import pygame

        pygame.init()
        if sys.platform in ("emscripten", "wasi"):
            _configure_web_page()
        screen = pygame.display.set_mode((_WEB_W, _WEB_H))
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
