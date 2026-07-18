# ARCHITECTURE — WOZ.exe

## Producto

Paquete único `src/aventura_woz/`: aventura SCUMM con puzzles = estructuras de datos.  
No depende del visualizador `ds_visualizer` (proyecto hermano / origen pedagógico).

## Capas

| Módulo | Rol |
|---|---|
| `main.py` | Loop pygame (ventana, FPS) |
| `game.py` | Input SCUMM, debug `Ctrl+A`, mute `M` |
| `world.py` | Salas, hotspots, puzzles, flags |
| `scenes.py` | Fondos PNG + overlays / hitboxes |
| `render.py` | Canvas 640×400, UI verbos/inventario/status |
| `scumm.py` | Verbos, sentence line, back button |
| `state.py` | Estado de partida + fades |
| `audio.py` | Música por acto (chiptune o archivos en `audio/`) |
| `config.py` | Layout, paleta, volumen |
| `player.py` | Perfil (nombre / vibe / handle) |

## Decisiones

- **UI SCUMM** (verbos ES + hotspots), no menú Investigar/Mover.
- **TIME CREDITS**: solo fallos de puzzle; retry mantiene perfil.
- **Resolución lógica** 640×400 escalada nearest.
- **Arte**: PNGs en `imgs/`; si falta uno, placeholder jugable.
- **Música**: un tema por acto; `M` mute; se puede reemplazar con `.ogg`/`.mp3`.
- **Idioma**: ES en UI; guiños EN (HAL, boot).

## Web (pygbag)

- Entrada: `src/main.py` (loop `async` + `await asyncio.sleep(0)`).
- Mismo código que desktop; `sys.platform == "emscripten"` desactiva resize y el mixer WAV.
- Fuentes: `fonts.py` (fallback sin Consolas en WASM).
- **Trampa evitada:** no usar `import wave` (stdlib). Pygbag lo confunde con el
  paquete PyPI `wave` e intenta instalar dependencias → pantalla gris tras el loading.
  Los WAV se escriben a mano con `struct` si hace falta generarlos.
- Build: `python -m pygbag --build … src` → `src/build/web/`.
- CI: `.github/workflows/deploy-web.yml` → GitHub Pages.
