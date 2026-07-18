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
    try:
        from aventura_woz.main import main

        await main()
    except Exception:
        traceback.print_exc()
        # Evitar que el shell de pygbag cierre sin dejar ver el error
        if sys.platform in ("emscripten", "wasi"):
            while True:
                await asyncio.sleep(1)
        raise


asyncio.run(_boot())
