# SCRIPT — WOZ.exe Actos I–III (v0.6)

Complementa `GUION_AVENTURA_WOZ.md` v0.6.

## Flujo

```
splash → boot → perfil → Homebrew
  → STACK → QUEUE → Portal → Neon → HASH
  → Cantina (SET) → Maze (BFS) → HAL ante (UF) → act2_end
  → Bahía (PQ) → Trie → Núcleo (Heap) → Ending
```

## Controles

| Input | Uso |
|---|---|
| Click verbo + objeto | SCUMM |
| ◀ Volver / `BACKSPACE` | Sala padre |
| `1`–`9` | Menú |
| `H` | Hint |
| `M` | Mute / unmute música |
| `ESC` | Pause |
| `Ctrl+A` | Debug skip |
| `Ctrl+Q` | Salir |

## Acto III — soluciones

1. **Bahía:** Usar P1 WOZ → P2 CREW → P3 CARGO  
2. **Trie:** Usar/Ir a W → O → Z  
3. **Núcleo:** Usar MEMORY → LOGIC → EYE → Abrir Cápsula  

## Assets

| Archivo | Sala |
|---|---|
| `evac.png` | Bahía |
| `trie.png` | Lab Trie |
| `hal_core.png` | Núcleo |
| `ending.png` | Epílogo |
