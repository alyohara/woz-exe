"""Renderer SCUMM: escena arriba + verbos/inventario abajo (Maniac Mansion)."""

from __future__ import annotations

import pygame

from aventura_woz import config
from aventura_woz import gfx
from aventura_woz.fonts import make_font
from aventura_woz.scumm import back_button_rect, inventory_rects, verb_grid_rects
from aventura_woz.state import GameState
from aventura_woz.world import RoomView


class Renderer:
    def __init__(self) -> None:
        self._font = None
        self._font_title = None
        self._font_small = None
        self._font_verb = None
        self._canvas = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H))
        self.last_scale = 1
        self.last_offset = (0, 0)
        self.menu_option_rects: list[pygame.Rect] = []

    def _ensure_fonts(self) -> None:
        if self._font is None:
            self._font = make_font(config.FONT_SIZE)
            self._font_title = make_font(config.FONT_SIZE_TITLE, bold=True)
            self._font_small = make_font(config.FONT_SIZE_SMALL)
            self._font_verb = make_font(config.FONT_SIZE_VERB, bold=True)

    def screen_to_logical(self, mx: int, my: int) -> tuple[int, int] | None:
        ox, oy = self.last_offset
        scale = self.last_scale
        if scale <= 0:
            return None
        lx = int((mx - ox) / scale)
        ly = int((my - oy) / scale)
        if 0 <= lx < config.LOGICAL_W and 0 <= ly < config.LOGICAL_H:
            return lx, ly
        return None

    def draw(
        self,
        screen: pygame.Surface,
        room: RoomView,
        state: GameState,
        width: int,
        height: int,
    ) -> None:
        self._ensure_fonts()
        self.menu_option_rects = []
        c = self._canvas
        c.fill(config.BG)

        sh = config.scene_h(room.use_scumm)
        sy = config.sentence_y(room.use_scumm)
        ut = config.ui_top(room.use_scumm)

        # --- Escena ---
        scene = pygame.Rect(0, 0, config.LOGICAL_W, sh)
        gfx.rect(c, 0, 0, scene.w, scene.h, config.PANEL_FILL)
        if room.draw_art:
            room.draw_art(c, scene, state)

        # Etiquetas visibles en salidas (para no perderse)
        if room.use_scumm:
            self._draw_exit_labels(c, room)

        # Caption SCUMM: franja baja de la escena (no caja modal)
        if state.feedback and room.use_scumm:
            self._draw_feedback_caption(c, state.feedback, sh)

        if state.hint_on:
            tip = self._font_small.render(
                f"PISTA> {room.hint[:58]}", True, config.YELLOW
            )
            bg = pygame.Surface((tip.get_width() + 8, tip.get_height() + 4))
            bg.fill(config.BG)
            c.blit(bg, (4, 4))
            c.blit(tip, (8, 6))

        # --- Sentence ---
        gfx.rect(c, 0, sy, config.LOGICAL_W, config.SENTENCE_H, config.BG)
        sentence = state.sentence if room.use_scumm else room.title
        c.blit(
            self._font_small.render(sentence[:72], True, config.SENTENCE_COLOR),
            (8, sy + 1),
        )
        gfx.hline(c, 0, ut - 1, config.LOGICAL_W, config.GRAY_DIM)

        # --- Panel UI ---
        gfx.rect(
            c,
            0,
            ut,
            config.LOGICAL_W,
            config.LOGICAL_H - ut - config.STATUS_H,
            config.BG,
        )

        if room.use_scumm:
            self._draw_scumm_ui(c, room, state)
        else:
            self._draw_menu_ui(c, room, state, ut)

        # --- Status ---
        gfx.rect(
            c,
            0,
            config.LOGICAL_H - config.STATUS_H,
            config.LOGICAL_W,
            config.STATUS_H,
            (0, 0, 20),
        )
        who = state.player.display_name if state.player.name else "???"
        credit_color = config.RED if state.credits <= 1 else config.PHOSPHOR
        status = (
            f" CR:{state.credits}  {who}  | H:pista M:musica ESC:pausa | {room.title}"
        )
        c.blit(
            self._font_small.render(status[:78], True, credit_color),
            (4, config.LOGICAL_H - config.STATUS_H + 1),
        )

        if state.paused:
            self._draw_pause(c)

        gfx.draw_scanlines(c, config.SCANLINE_ALPHA)

        if state.transition_alpha > 0:
            overlay = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H))
            overlay.fill(config.BG)
            overlay.set_alpha(int(state.transition_alpha))
            c.blit(overlay, (0, 0))

        screen.fill(config.BG)
        scale = min(width / config.LOGICAL_W, height / config.LOGICAL_H)
        scale = max(scale, 0.5)
        self.last_scale = scale
        sw = max(1, int(config.LOGICAL_W * scale))
        sh_px = max(1, int(config.LOGICAL_H * scale))
        ox, oy = (width - sw) // 2, (height - sh_px) // 2
        self.last_offset = (ox, oy)
        scaled = pygame.transform.scale(c, (sw, sh_px))
        screen.blit(scaled, (ox, oy))
        if scale >= 1.15:
            pygame.draw.rect(
                screen, config.PHOSPHOR_DIM, (ox - 2, oy - 2, sw + 4, sh_px + 4), 2
            )

    def _draw_exit_labels(self, c, room) -> None:
        """Chips «salir» sobre hotspots is_exit (excepto el hub)."""
        if room.room_id == "homebrew":
            return
        for hs in room.hotspots:
            if not hs.is_exit:
                continue
            # No etiquetar el propio portal de entrada gigante si no es vuelta
            label = hs.name
            if label.startswith("Bucket"):
                continue
            short = {
                "Homebrew": "◀ Taller",
                "Salida": "◀ Salida",
                "Calle": "◀ Calle",
                "Portal (vuelta)": "◀ Portal",
                "Portal": "▶ Portal",
            }.get(label, f"◀ {label}")
            surf = self._font_small.render(short, True, config.YELLOW)
            x = max(2, min(hs.rect.x, config.LOGICAL_W - surf.get_width() - 4))
            y = max(2, hs.rect.bottom - 14)
            if y + 14 > config.scene_h(True):
                y = max(2, hs.rect.top)
            bg = pygame.Surface((surf.get_width() + 6, surf.get_height() + 2))
            bg.fill(config.BG)
            bg.set_alpha(200)
            c.blit(bg, (x - 2, y - 1))
            c.blit(surf, (x, y))

    def _draw_scumm_ui(self, c, room, state) -> None:
        panel_bottom = config.LOGICAL_H - config.STATUS_H
        inv_y = panel_bottom - config.VERB_ROWS_H
        for hit in verb_grid_rects(True):
            col = (
                config.VERB_SELECTED
                if hit.verb == state.selected_verb
                else config.VERB_COLOR
            )
            c.blit(self._font_verb.render(hit.verb, True, col), hit.rect.topleft)

        c.blit(
            self._font_small.render("Inventario", True, config.GRAY),
            (520, inv_y),
        )
        for item, r in inventory_rects(state.player.inventory, True):
            col = (
                config.VERB_SELECTED
                if item == state.selected_item
                else config.INV_COLOR
            )
            label = item if len(item) < 14 else item[:12] + ".."
            c.blit(self._font_small.render(label, True, col), r.topleft)

        if room.back_room:
            br = back_button_rect()
            gfx.rect(c, br.x, br.y, br.w, br.h, (40, 40, 0))
            gfx.rect(c, br.x, br.y, br.w, br.h, config.YELLOW, 1)
            c.blit(
                self._font_small.render("◀ Volver", True, config.YELLOW),
                (br.x + 8, br.y + 1),
            )

    def _draw_menu_ui(self, c, room, state, ut: int) -> None:
        """Texto arriba del panel; opciones ancladas abajo (sin solaparse)."""
        n_opts = 0 if state.mode in ("type_name", "type_handle") else len(room.options)
        opts_block = n_opts * config.MENU_OPT_H + (8 if n_opts else 0)
        opts_top = config.LOGICAL_H - config.STATUS_H - opts_block
        text_top = ut + 4
        text_bottom = opts_top - 6

        body = state.feedback.strip() if state.feedback.strip() else room.narration
        self._blit_wrapped(
            c,
            body,
            10,
            text_top,
            config.LOGICAL_W - 20,
            config.PHOSPHOR,
            text_bottom,
        )

        if state.mode in ("type_name", "type_handle"):
            tip = self._font_small.render(
                "Escribí + ENTER  |  BACKSPACE borra (vacío = atrás)",
                True,
                config.YELLOW,
            )
            c.blit(tip, (10, config.LOGICAL_H - config.STATUS_H - 18))
            return

        for i, opt in enumerate(room.options[: config.MENU_OPT_MAX]):
            y = opts_top + i * config.MENU_OPT_H
            label = f"[{i + 1}]  {opt.label}"
            if len(label) > 72:
                label = label[:69] + "..."
            r = pygame.Rect(8, y, config.LOGICAL_W - 16, config.MENU_OPT_H - 1)
            self.menu_option_rects.append(r)
            gfx.rect(c, r.x, r.y, r.w, r.h, (0, 30, 0))
            c.blit(self._font.render(label, True, config.WHITE), (12, y + 1))

    def _draw_feedback_caption(self, c, text: str, scene_h: int) -> None:
        """Diálogo estilo SCUMM: franja baja, no caja modal gigante."""
        lines: list[str] = []
        for para in text.replace("\n", " ").split("  "):
            para = para.strip()
            if not para:
                continue
            while len(para) > 62:
                cut = para.rfind(" ", 0, 62)
                if cut < 20:
                    cut = 62
                lines.append(para[:cut].strip())
                para = para[cut:].strip()
            if para:
                lines.append(para)
        lines = lines[:3]
        if not lines:
            return

        line_h = 13
        pad = 4
        box_h = pad * 2 + len(lines) * line_h
        y0 = scene_h - box_h - 2
        # barra semitransparente
        bar = pygame.Surface((config.LOGICAL_W, box_h))
        bar.fill(config.BG)
        bar.set_alpha(220)
        c.blit(bar, (0, y0))
        gfx.hline(c, 0, y0, config.LOGICAL_W, config.CYAN_DIM)
        for i, line in enumerate(lines):
            surf = self._font_small.render(line, True, config.WHITE)
            c.blit(surf, ((config.LOGICAL_W - surf.get_width()) // 2, y0 + pad + i * line_h))

    def _blit_wrapped(self, screen, text, x, y, max_width, color, max_y) -> int:
        line_h = 15
        for paragraph in text.split("\n"):
            if y + line_h > max_y:
                if y < max_y:
                    screen.blit(
                        self._font_small.render("…", True, config.GRAY), (x, y)
                    )
                break
            if paragraph == "":
                y += line_h // 2
                continue
            words = paragraph.split(" ")
            line = ""
            for word in words:
                test = word if not line else f"{line} {word}"
                if self._font.size(test)[0] <= max_width:
                    line = test
                else:
                    if line:
                        screen.blit(self._font.render(line, True, color), (x, y))
                        y += line_h
                        if y + line_h > max_y:
                            return y
                    line = word
            if line and y + line_h <= max_y:
                screen.blit(self._font.render(line, True, color), (x, y))
                y += line_h
        return y

    def _draw_pause(self, canvas) -> None:
        overlay = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        canvas.blit(overlay, (0, 0))
        msg = self._font_title.render("PAUSA", True, config.YELLOW)
        canvas.blit(
            msg, msg.get_rect(center=(config.LOGICAL_W // 2, config.LOGICAL_H // 2 - 10))
        )
        sub = self._font.render("[ESC] seguir   [Q] salir", True, config.WHITE)
        canvas.blit(
            sub, sub.get_rect(center=(config.LOGICAL_W // 2, config.LOGICAL_H // 2 + 16))
        )
