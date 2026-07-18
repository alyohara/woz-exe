# WOZ.exe — Rescate en el Ciberespacio

Aventura gráfica **point-and-click** estilo SCUMM / Maniac Mansion, hecha con **pygame-ce**.  
Los acertijos enseñan estructuras de datos (pila, cola, hash, set, grafo, union-find, heap, trie…).

**Leonardo Bianco** presenta · inspirado en la programación de **Flavio Speche**.

---

## Tecnologías

- Python 3.11+
- [pygame-ce](https://pyga.game/) 2.5.7

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```powershell
cd src
python -m aventura_woz
```

## Controles

| Input | Acción |
|---|---|
| Click verbo + objeto | Acción SCUMM |
| ◀ Volver / `BACKSPACE` | Sala padre |
| `H` | Pista |
| `M` | Mute / unmute música |
| `ESC` | Pausa |
| `Ctrl+A` | Debug: saltar pantalla (como resuelta) |
| `Ctrl+Q` | Salir |
| `1`–`9` | Menús (splash / perfil / finales) |

## Historia (resumen)

1. **Acto I** — Homebrew: STACK → QUEUE → Portal → Neon → HASH  
2. **Acto II** — Cantina (SET) → Laberinto (grafo/BFS) → Antecámara (Union-Find)  
3. **Acto III** — Bahía (Priority Queue) → Trie → Núcleo HAL (Heap) → Epílogo  

## Estructura del repo

```
src/aventura_woz/   # código del juego
  imgs/             # fondos pixel-art
  audio/            # temas (chiptune o tus .ogg/.mp3)
docs/               # guion y script
```

## Documentación

- `docs/GUION_AVENTURA_WOZ.md` — diseño narrativo  
- `docs/SCRIPT_VERTICAL_SLICE.md` — flujo / controles  
- `ARCHITECTURE.md` — decisiones técnicas  
- `src/aventura_woz/audio/README.md` — cómo poner tu música  

## Créditos

- Diseño y desarrollo del juego: **Leonardo Bianco**  
- Inspiración / base pedagógica en estructuras de datos: **Flavio Speche**  
