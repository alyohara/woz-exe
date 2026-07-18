# GUION — Aventura: «WOZ.exe: Rescate en el Ciberespacio»

> Documento de diseño narrativo **v0.6**  
> Rama: `feature/aventura-woz-hal`  
> Producto: `src/aventura_woz/`  
> Jugabilidad: **SCUMM** — verbos + hotspots; hints **H**; Volver / `BACKSPACE`; debug `Ctrl+A`.

---

## 0. Decisiones (cerradas)

| # | Tema | Decisión |
|---|---|---|
| 1 | Integración | `src/aventura_woz/` |
| 2 | Fallos | TIME CREDITS; retry mantiene perfil |
| 3 | Idioma | ES UI; guiños EN (HAL) |
| 4 | Humor | Maniac / DOTT + refs 80–90 |

Créditos: base 3; +1 al abrir Acto II (HASH) y +1 al entrar Acto III (cap 5).

---

## 1. Pitch

Woz desapareció. `FIND WOZ. HAL KNOWS.` Rescate vía estructuras de datos.

---

## 2. Mapa completo

### Acto I
```
Homebrew → STACK → QUEUE → Portal → Neon → HASH → neon_door_open
```

### Acto II
```
Neon → Cantina (SET) → Laberinto (BFS) → Antecámara (Union-Find) → act2_end
```

### Acto III
```
act2_end → Continuar
  → BAHÍA · PRIORITY QUEUE   (P1 WOZ → P2 CREW → P3 CARGO)
  → LAB · TRIE               (W → O → Z)
  → NÚCLEO · HEAP            (MEMORY → LOGIC → EYE)
  → EPÍLOGO                  (Woz libre)
```

---

## 3. Puzzles Acto III

| Sala | Estructura | Solución |
|---|---|---|
| Bahía | **Priority Queue / Heap** | Usar cápsulas P1 → P2 → P3 |
| Lab Prefijos | **Trie** | Letras W → O → Z (A/X fallan) |
| Núcleo HAL | **Heap (extract-min)** | Apagar MEMORY → LOGIC → EYE |

### Flags

| Flag | Significado |
|---|---|
| `heap_ok` | Evacuación en orden |
| `trie_ok` | Prefijo WOZ completo |
| `core_ok` | HAL apagado |
| `ending_seen` | Epílogo |

Estado: `evac_step`, `trie_prefix`, `core_step`.

### NPCs

| NPC | Rol |
|---|---|
| Cap. Queue | Explica extract-min |
| Maestro Byte | Guía del trie |
| HAL | Boss / amenazas EN |
| Woz | Eco en cápsula + epílogo |

---

## 4. Assets pendientes Acto III

| Archivo | Sala |
|---|---|
| `evac.png` | Bahía · Priority Queue |
| `trie.png` | Lab · Trie |
| `hal_core.png` | Núcleo HAL |
| `ending.png` | Epílogo |

Sin PNG: placeholder + overlays clickeables.

---

## 5. Referencias

- Script: `docs/SCRIPT_VERTICAL_SLICE.md`
- Código: `world.py`, `scenes.py`, `game.py`

---

*v0.6 — Acto III jugable (PQ · Trie · Heap) + epílogo.*
