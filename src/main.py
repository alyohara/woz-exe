"""Entrada para pygbag (carpeta `src/` = app web).

Desktop:
  cd src && python main.py
  cd src && python -m aventura_woz

Web (local):
  python -m pygbag --ume_block 0 src
"""

from __future__ import annotations

import asyncio

from aventura_woz.main import main

asyncio.run(main())
