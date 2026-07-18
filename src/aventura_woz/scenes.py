"""Escenas con fondos pixel-art en imgs/."""

from __future__ import annotations

from pathlib import Path

import pygame

from aventura_woz import config
from aventura_woz.state import GameState

_IMGS = Path(__file__).resolve().parent / "imgs"
_bg_cache: dict[tuple[str, int, int], pygame.Surface] = {}


def _ticks() -> int:
    return pygame.time.get_ticks()


def _scale_cover(src: pygame.Surface, tw: int, th: int) -> pygame.Surface:
    """Escala cover y recorta al centro (sin distorsión)."""
    sw, sh = src.get_size()
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    scaled = pygame.transform.scale(src, (nw, nh))
    ox, oy = (nw - tw) // 2, (nh - th) // 2
    return scaled.subsurface((ox, oy, tw, th)).copy()


def get_bg(filename: str, scene_w: int, scene_h: int) -> pygame.Surface:
    """Fondo cacheado; si falta el PNG, placeholder con título."""
    key = (filename, scene_w, scene_h)
    if key not in _bg_cache:
        path = _IMGS / filename
        if path.exists():
            raw = pygame.image.load(str(path)).convert()
            _bg_cache[key] = _scale_cover(raw, scene_w, scene_h)
        else:
            surf = pygame.Surface((scene_w, scene_h))
            surf.fill((12, 8, 28))
            for y in range(0, scene_h, 4):
                pygame.draw.line(surf, (20, 14, 40), (0, y), (scene_w, y))
            label = filename.replace(".png", "").upper()
            font = pygame.font.SysFont(config.FONT_FAMILY, 18, bold=True)
            t = font.render(f"[PENDIENTE] {label}", True, config.CYAN)
            surf.blit(t, t.get_rect(center=(scene_w // 2, scene_h // 2 - 10)))
            tip = pygame.font.SysFont(config.FONT_FAMILY, 12).render(
                "Generá el PNG y ponelo en imgs/", True, config.GRAY
            )
            surf.blit(tip, tip.get_rect(center=(scene_w // 2, scene_h // 2 + 16)))
            _bg_cache[key] = surf
    return _bg_cache[key]


def _blit_bg(clip: pygame.Surface, filename: str) -> None:
    clip.blit(get_bg(filename, clip.get_width(), clip.get_height()), (0, 0))


# --- Hitboxes (coords sobre crop cover 640×H) ---


def homebrew_rects(scene_h: int | None = None) -> dict[str, pygame.Rect]:
    """Hitboxes alineadas a background1.png (640×336)."""
    return {
        "Apple II": pygame.Rect(90, 158, 92, 82),
        "PROTO-G": pygame.Rect(202, 224, 46, 46),
        "Banco": pygame.Rect(308, 150, 55, 65),
        "Nota": pygame.Rect(358, 75, 60, 48),
        "Herramientas": pygame.Rect(415, 208, 75, 45),
        # Módem en estante alto; Portal = óvalo (sin solaparse)
        "Módem": pygame.Rect(538, 55, 85, 40),
        "Portal": pygame.Rect(455, 75, 78, 145),
        "Ventana": pygame.Rect(100, 32, 58, 68),
    }


def stack_rects() -> dict[str, pygame.Rect]:
    return {
        "Tarjeta TOPE": pygame.Rect(255, 115, 130, 48),
        "Base de la pila": pygame.Rect(255, 185, 130, 48),
        "Salida": pygame.Rect(8, 285, 110, 40),
    }


def modem_rects() -> dict[str, pygame.Rect]:
    return {
        "Modem": pygame.Rect(28, 155, 190, 130),
        "Cola correcta": pygame.Rect(250, 170, 290, 75),
        "Orden incorrecto": pygame.Rect(480, 265, 140, 50),
        "Homebrew": pygame.Rect(8, 285, 120, 40),
        "Portal": pygame.Rect(520, 40, 100, 80),
    }


def portal_rects() -> dict[str, pygame.Rect]:
    return {
        "Portal": pygame.Rect(340, 25, 270, 250),
        "Homebrew": pygame.Rect(8, 285, 120, 40),
    }


def neon_rects() -> dict[str, pygame.Rect]:
    """Alineado a neon.png (crop 640×336)."""
    return {
        "Cantina": pygame.Rect(170, 95, 120, 175),
        "Lora": pygame.Rect(390, 130, 100, 170),
        "Puerta de acero": pygame.Rect(490, 95, 130, 185),
        "Portal (vuelta)": pygame.Rect(8, 285, 140, 40),
    }


def hash_bucket_rects() -> list[pygame.Rect]:
    """Buckets 0..6 sobre hash.png."""
    start_x, y, w, h, step = 115, 175, 54, 72, 63
    return [pygame.Rect(start_x + i * step, y, w, h) for i in range(7)]


def hash_exit_rect() -> pygame.Rect:
    return pygame.Rect(8, 285, 110, 40)


def cantina_rects() -> dict[str, pygame.Rect]:
    """Badges en fila + bartender + puerta laberinto (cantina.png)."""
    return {
        "SPOOF": pygame.Rect(40, 135, 70, 70),
        "NULLPTR": pygame.Rect(115, 135, 70, 70),
        "HALFAN": pygame.Rect(190, 135, 70, 70),
        "GUEST99": pygame.Rect(250, 140, 70, 60),
        "WOZ": pygame.Rect(320, 135, 70, 70),
        "Bartender": pygame.Rect(520, 80, 110, 200),
        "Laberinto": pygame.Rect(430, 70, 90, 180),
        "Neon": pygame.Rect(8, 285, 130, 40),
    }


def maze_rects() -> dict:
    """Nodos del grafo en maze.png + salida a cantina."""
    nodes = {
        0: pygame.Rect(45, 245, 95, 75),
        1: pygame.Rect(195, 90, 85, 70),
        2: pygame.Rect(285, 235, 85, 70),
        3: pygame.Rect(430, 90, 85, 70),
        4: pygame.Rect(515, 155, 100, 85),
    }
    return {"nodes": nodes, "Cantina": pygame.Rect(8, 285, 120, 40)}


def hal_rects() -> dict[str, pygame.Rect]:
    """Cajas UNION + cápsula + ojo (hal_ante.png)."""
    return {
        "Union AC": pygame.Rect(35, 65, 170, 60),
        "Union BC": pygame.Rect(35, 140, 170, 60),
        "Union AB": pygame.Rect(35, 215, 170, 60),
        "Capsula": pygame.Rect(400, 45, 185, 270),
        "HAL": pygame.Rect(250, 0, 110, 75),
        "Maze": pygame.Rect(8, 285, 120, 40),
    }


def evac_rects() -> dict[str, pygame.Rect]:
    """Bahía — pods P1/P2/P3 + Capitan + puerta Trie (evac.png)."""
    return {
        "P1": pygame.Rect(45, 85, 165, 185),
        "P2": pygame.Rect(230, 95, 155, 175),
        "P3": pygame.Rect(400, 105, 140, 165),
        "Captain": pygame.Rect(290, 255, 130, 75),
        "Trie": pygame.Rect(530, 70, 100, 200),
    }


def trie_rects() -> dict[str, pygame.Rect]:
    """Nodos del trie + Byte + salidas (trie.png)."""
    return {
        "W": pygame.Rect(285, 30, 75, 60),
        "O": pygame.Rect(240, 130, 75, 60),
        "Z": pygame.Rect(285, 245, 75, 60),
        "A": pygame.Rect(400, 130, 75, 60),
        "X": pygame.Rect(480, 230, 75, 60),
        "Byte": pygame.Rect(15, 75, 130, 165),
        "Core": pygame.Rect(525, 55, 105, 200),
        "Evac": pygame.Rect(15, 255, 110, 65),
    }


def core_rects() -> dict[str, pygame.Rect]:
    """Paneles EYE/MEMORY/LOGIC + cápsula (hal_core.png)."""
    return {
        # Arte: arriba EYE P3, medio MEMORY P1, abajo LOGIC P2
        "EYE": pygame.Rect(55, 70, 145, 70),
        "MEMORY": pygame.Rect(55, 155, 145, 70),
        "LOGIC": pygame.Rect(55, 240, 145, 70),
        "Capsula": pygame.Rect(400, 45, 185, 260),
        "Trie": pygame.Rect(8, 285, 120, 40),
    }


# --- Draws ---


def draw_splash(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "splash.png")
    cx = rect.width // 2
    f = pygame.font.SysFont(config.FONT_FAMILY, 14, bold=True)
    line1 = f.render("Leonardo Bianco", True, config.YELLOW)
    shadow = f.render("Leonardo Bianco", True, config.BG)
    clip.blit(shadow, line1.get_rect(center=(cx + 1, 18)))
    clip.blit(line1, line1.get_rect(center=(cx, 17)))
    line2 = pygame.font.SysFont(config.FONT_FAMILY, 12).render(
        "presenta", True, config.WHITE
    )
    clip.blit(line2, line2.get_rect(center=(cx, 34)))
    big = pygame.font.SysFont(config.FONT_FAMILY, 22, bold=True)
    title = big.render("WOZ.exe", True, config.PHOSPHOR)
    clip.blit(title, title.get_rect(center=(cx, 58)))
    credit = pygame.font.SysFont(config.FONT_FAMILY, 11).render(
        "inspirado en la programación de Flavio Speche", True, config.CYAN
    )
    clip.blit(credit, credit.get_rect(center=(cx, 80)))
    tip = pygame.font.SysFont(config.FONT_FAMILY, 11).render(
        "Click o ENTER para continuar…", True, config.GRAY
    )
    if (_ticks() // 500) % 2 == 0:
        clip.blit(tip, tip.get_rect(center=(cx, rect.height - 14)))


def draw_boot(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "boot.png")


def draw_profile(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "profile.png")
    # Input sobre el CRT del Apple //e
    box = pygame.Rect(210, 58, 260, 28)
    pygame.draw.rect(clip, config.BG, box)
    pygame.draw.rect(clip, config.PHOSPHOR, box, 2)
    buf = state.typing_buffer
    buf = buf + ("█" if (_ticks() // 350) % 2 == 0 else "_")
    tf = pygame.font.SysFont(config.FONT_FAMILY, 14)
    clip.blit(tf.render(buf[:28], True, config.PHOSPHOR), (box.x + 8, box.y + 6))


def draw_homebrew(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "background1.png")
    if state.has("queue_ok"):
        portal = homebrew_rects()["Portal"]
        color = config.CYAN if (_ticks() // 200) % 2 == 0 else config.WHITE
        pygame.draw.ellipse(clip, color, portal.inflate(-6, -6), 2)


def draw_stack(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "stack.png")


def draw_modem(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "modem.png")
    if state.has("key_inserted") or state.has("queue_ok"):
        pygame.draw.circle(clip, config.PHOSPHOR, (95, 200), 4)
    elif state.has("has_grid_key"):
        pygame.draw.circle(clip, config.RED, (95, 200), 4)


def draw_portal(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "portal.png")
    if state.has("queue_ok"):
        pr = portal_rects()["Portal"]
        color = config.CYAN if (_ticks() // 180) % 2 == 0 else config.WHITE
        pygame.draw.ellipse(clip, color, pr.inflate(-20, -30), 2)


def draw_neon(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "neon.png")
    if state.has("neon_door_open"):
        door = neon_rects()["Cantina"]
        color = config.ORANGE if (_ticks() // 220) % 2 == 0 else config.YELLOW
        pygame.draw.rect(clip, color, door.inflate(-12, -16), 2)


def draw_hash(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "hash.png")


def draw_cantina(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "cantina.png")
    cr = cantina_rects()
    # Cruz sobre IDs ya baneados (el arte los deja visibles)
    for badge in state.banned_ids:
        if badge not in cr:
            continue
        r = cr[badge]
        pygame.draw.line(clip, config.RED, r.topleft, r.bottomright, 3)
        pygame.draw.line(clip, config.RED, r.topright, r.bottomleft, 3)
    if state.has("set_ok"):
        color = config.YELLOW if (_ticks() // 200) % 2 == 0 else config.ORANGE
        pygame.draw.rect(clip, color, cr["Laberinto"].inflate(-6, -10), 2)


def draw_maze(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "maze.png")
    # Solo resalta el nodo actual (el arte ya trae aristas y labels)
    r = maze_rects()["nodes"].get(state.maze_pos)
    if r is not None:
        col = config.YELLOW if (_ticks() // 250) % 2 == 0 else config.WHITE
        pygame.draw.rect(clip, col, r.inflate(6, 6), 2)


def draw_hal_ante(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "hal_ante.png")
    hr = hal_rects()
    if state.hal_step >= 1 or state.has("hal_ok"):
        pygame.draw.rect(clip, config.PHOSPHOR, hr["Union AC"].inflate(4, 4), 2)
    if state.has("hal_ok"):
        pygame.draw.rect(clip, config.PHOSPHOR, hr["Union BC"].inflate(4, 4), 2)
        pygame.draw.rect(clip, config.CYAN, hr["Capsula"].inflate(-8, -12), 2)


def draw_act2_end(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    fname = "act2_end.png" if (_IMGS / "act2_end.png").exists() else "slice_end.png"
    _blit_bg(clip, fname)


def draw_slice_end(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    draw_act2_end(surface, rect, state)


def draw_evac(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "evac.png")
    er = evac_rects()
    # Marca pods ya extraídos
    for need, key in enumerate(("P1", "P2", "P3")):
        if state.evac_step > need or state.has("heap_ok"):
            r = er[key]
            pygame.draw.line(clip, config.GRAY, r.topleft, r.bottomright, 2)
            pygame.draw.line(clip, config.GRAY, r.topright, r.bottomleft, 2)
    if state.has("heap_ok"):
        color = config.CYAN if (_ticks() // 200) % 2 == 0 else config.YELLOW
        pygame.draw.rect(clip, color, er["Trie"].inflate(-8, -20), 2)


def draw_trie(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "trie.png")
    tr = trie_rects()
    pref = state.trie_prefix
    target = "WOZ"
    for i, letter in enumerate(target):
        r = tr[letter]
        if len(pref) > i:
            pygame.draw.rect(clip, config.YELLOW, r.inflate(4, 4), 2)
        elif len(pref) == i and not state.has("trie_ok"):
            col = config.WHITE if (_ticks() // 250) % 2 == 0 else config.PHOSPHOR
            pygame.draw.rect(clip, col, r.inflate(4, 4), 2)
    if state.has("trie_ok"):
        color = config.RED if (_ticks() // 200) % 2 == 0 else config.ORANGE
        pygame.draw.rect(clip, color, tr["Core"].inflate(-8, -16), 2)


def draw_hal_core(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "hal_core.png")
    cr = core_rects()
    order = ("MEMORY", "LOGIC", "EYE")
    for i, key in enumerate(order):
        if state.core_step > i or state.has("core_ok"):
            r = cr[key]
            pygame.draw.line(clip, config.GRAY, r.topleft, r.bottomright, 2)
            pygame.draw.line(clip, config.GRAY, r.topright, r.bottomleft, 2)
        elif state.core_step == i:
            col = config.YELLOW if (_ticks() // 250) % 2 == 0 else config.WHITE
            pygame.draw.rect(clip, col, cr[key].inflate(4, 4), 2)
    if state.has("core_ok"):
        pygame.draw.rect(clip, config.CYAN, cr["Capsula"].inflate(-10, -14), 2)


def draw_ending(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    fname = "ending.png" if (_IMGS / "ending.png").exists() else "act2_end.png"
    _blit_bg(clip, fname)

def draw_game_over(surface: pygame.Surface, rect: pygame.Rect, state: GameState) -> None:
    clip = surface.subsurface(rect)
    _blit_bg(clip, "game_over.png")
    f = pygame.font.SysFont(config.FONT_FAMILY, 20, bold=True)
    t = f.render("TIME CREDITS: 0", True, config.RED)
    clip.blit(t, t.get_rect(center=(rect.width // 2, rect.height // 2 + 40)))
