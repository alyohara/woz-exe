# WOZ.exe — Rescate en el Ciberespacio

Aventura gráfica **point-and-click** al estilo **SCUMM / Maniac Mansion**, hecha con **pygame-ce**.  
Steve Wozniak desapareció del laboratorio Homebrew. Un Apple II solo murmura:

> `FIND WOZ. HAL KNOWS.`

Para rescatarlo hay que pensar con **estructuras de datos**: pila, cola, hash, set, grafo, union-find, heap, trie…

**Leonardo Bianco** presenta · inspirado en la programación de **Flavio Speche**.

---

## Qué es

Un juego corto (3 actos + epílogo) donde:

- Explorás hubs con **verbos** (Ir a, Mirar, Usar, Hablar…) y **hotspots** clickeables
- Cada acertijo enseña una estructura sin ser un tutorial seco
- El tono es humor seco 80s/90s (Maniac Mansion / DOTT) con guiños a HAL, Tron, Blade Runner, etc.
- Hay **créditos de tiempo**: fallar un puzzle gasta uno; a 0, game over (podés reintentar con el mismo perfil)

No es un visualizador de estructuras: es una **aventura** que las usa como mecánicas.

---

## Tecnologías / librerías

| Tecnología | Uso |
|---|---|
| **Python 3.11+** | Lenguaje |
| **[pygame-ce](https://pyga.game/) 2.5.7** | Gráficos, input, audio (`import pygame`) |
| Pixel art propio | Fondos en `src/aventura_woz/imgs/` |
| Audio procedural + archivos | Temas chiptune en `audio/` (reemplazables) |

Sin otras dependencias externas.

---

## Instalación

```powershell
git clone https://github.com/alyohara/woz-exe.git
cd woz-exe
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS:

```bash
git clone https://github.com/alyohara/woz-exe.git
cd woz-exe
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Cómo jugar

```powershell
cd src
python -m aventura_woz
```

1. Elegí un **verbo** abajo (Ir a, Mirar, Usar…).
2. Clickeá un **objeto** o salida en la escena.
3. La línea magenta arma la frase: `Usar GRID-01 con Módem`.
4. Si te trabás: **`H`** muestra la pista de la sala.

### Controles

| Input | Acción |
|---|---|
| Click verbo | Selecciona verbo |
| Click objeto / salida | Aplica el verbo (o entra a otra sala) |
| Click inventario | Selecciona ítem (fuerza **Usar**) |
| ◀ Volver / `BACKSPACE` | Vuelve a la sala padre |
| `H` | Alterna pista |
| `M` | Mute / unmute música |
| `ESC` | Pausa / despausa |
| `1`–`9` | Opciones en menús (splash, perfil, finales) |
| Letras + Enter | Nombre / handle al crear perfil |
| `Ctrl+A` | Debug: avanza como si resolviste la pantalla |
| `Ctrl+Q` | Salir |

---

## Funcionalidades

### Jugabilidad

- UI **SCUMM**: verbos en español, sentence line, inventario, cursor mano sobre hotspots
- Creación de personaje: **nombre**, **vibe** (garage / operador / arcade / campus) y **handle**
- **TIME CREDITS** (3 de base; bonos al avanzar de acto, tope 5)
- Transiciones con fade entre salas
- Música por acto; tecla **M** para silenciar
- `Ctrl+A` para probar el flujo completo sin resolver cada puzzle

### Acto I — La llamada Homebrew

| Puzzle | Estructura | Idea |
|---|---|---|
| Banco de trabajo | **Stack (LIFO)** | Sacá la tarjeta del tope → `GRID-01` |
| Módem | **Queue (FIFO)** | Encolá el mensaje en orden |
| Puerta Neon | **Hash map** | `hash("WOZ")` → bucket correcto |

### Acto II — Portales VHS

| Puzzle | Estructura | Idea |
|---|---|---|
| Cantina | **Set** | Banear impostores; no banear `WOZ` |
| Laberinto | **Grafo / BFS** | Camino `0 → 1 → 3 → 4` |
| Antecámara | **Union-Find** | Unir `A–C`, luego `B–C` |

### Acto III — Núcleo HAL

| Puzzle | Estructura | Idea |
|---|---|---|
| Bahía de escape | **Priority queue / Heap** | Extraer `P1 → P2 → P3` |
| Lab de prefijos | **Trie** | Formar `W → O → Z` |
| Núcleo | **Heap (extract-min)** | Apagar `MEMORY → LOGIC → EYE` |

Luego: **epílogo** (Woz libre).

---

## Estructura del repositorio

```
woz-exe/
├── README.md
├── ARCHITECTURE.md      # decisiones técnicas
├── AGENTS.md            # convenciones para desarrollo
├── requirements.txt
├── docs/
│   ├── GUION_AVENTURA_WOZ.md
│   └── SCRIPT_VERTICAL_SLICE.md
└── src/
    └── aventura_woz/    # el juego
        ├── imgs/        # fondos pixel-art
        ├── audio/       # temas (.wav generados o tus .ogg/.mp3)
        ├── world.py     # salas y puzzles
        ├── game.py      # input / loop SCUMM
        └── ...
```

---

## Personalizar música

Los temas chiptune se generan solos la primera vez. Para usar tu propia música, poné archivos en `src/aventura_woz/audio/`:

| Nombre sugerido | Cuándo suena |
|---|---|
| `theme_boot.ogg` | Splash / boot / perfil |
| `theme_act1.ogg` | Homebrew y Acto I |
| `theme_act2.ogg` | Neon / Cantina / Maze |
| `theme_act3.ogg` | Bahía / Trie / Núcleo |
| `theme_ending.ogg` | Epílogo |
| `theme_gameover.ogg` | Sin créditos |

Prioridad de formato: `.ogg` → `.mp3` → `.wav`. Más detalle en `src/aventura_woz/audio/README.md`.

---

## Documentación extra

| Archivo | Contenido |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Capas del código y decisiones de diseño |
| [`docs/GUION_AVENTURA_WOZ.md`](docs/GUION_AVENTURA_WOZ.md) | Guion narrativo completo |
| [`docs/SCRIPT_VERTICAL_SLICE.md`](docs/SCRIPT_VERTICAL_SLICE.md) | Flujo corto + checklist |

---

## Créditos

| | |
|---|---|
| **Diseño y desarrollo** | Leonardo Bianco |
| **Inspiración / base pedagógica** | Flavio Speche (estructuras de datos con Pygame) |

---

## Licencia / uso

Proyecto educativo y de portfolio. Si lo forkeás o lo usás en clase, una mención se agradece.
