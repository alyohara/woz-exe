"""Orquestador WOZ.exe — teclado + mouse SCUMM + transiciones."""

from __future__ import annotations

import pygame

from aventura_woz import config
from aventura_woz.audio import MusicPlayer
from aventura_woz.render import Renderer
from aventura_woz.scumm import back_button_rect, inventory_rects, verb_grid_rects
from aventura_woz.state import GameState
from aventura_woz.world import World


class Game:
    def __init__(self) -> None:
        self.state = GameState()
        self.world = World()
        self.renderer = Renderer()
        self.music = MusicPlayer()
        self._music_room = ""

    def current_view(self):
        return self.world.view(self.state)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.state.running = False
            elif event.type == pygame.MOUSEMOTION:
                if not self.state.blocking_input:
                    self._on_motion(event.pos)
                else:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.state.blocking_input:
                    self._on_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._on_key(event)

    def _on_key(self, event: pygame.event.Event) -> None:
        mods = pygame.key.get_mods()
        if event.key == pygame.K_q and (mods & pygame.KMOD_CTRL):
            self.state.running = False
            return
        if event.key == pygame.K_a and (mods & pygame.KMOD_CTRL):
            # Debug: avanzar como si el puzzle/pantalla actual estuviera resuelto
            self._debug_advance()
            return
        if event.key == pygame.K_m and not (mods & pygame.KMOD_CTRL):
            # Mute música (también durante pausa / tipeo)
            self.state.feedback = self.music.toggle_mute()
            return

        if self.state.paused:
            if event.key == pygame.K_ESCAPE:
                self.state.paused = False
                self.music.on_pause(False)
            elif event.key == pygame.K_q:
                self.state.running = False
            return

        # Durante fade-out no aceptar input de juego
        if self.state.transition_phase == "out":
            return

        if self.state.mode in ("type_name", "type_handle"):
            self._handle_typing(event)
            return

        if event.key == pygame.K_ESCAPE:
            self.state.paused = True
            self.music.on_pause(True)
        elif event.key == pygame.K_BACKSPACE:
            view = self.current_view()
            if view.use_scumm and view.back_room:
                self.state.goto(view.back_room, mode=view.back_mode)
                return
        elif event.key == pygame.K_h:
            self.state.hint_on = not self.state.hint_on
        elif event.key == pygame.K_RETURN and self.state.room_id == "splash":
            self.state.goto("boot", mode="explore")
        elif pygame.K_1 <= event.key <= pygame.K_9:
            view = self.current_view()
            if not view.use_scumm:
                idx = event.key - pygame.K_1
                if idx < len(view.options):
                    self.state.feedback = ""
                    view.options[idx].action(self.state)

    def _debug_advance(self) -> None:
        """Ctrl+A: salta al siguiente hito (solo para pruebas)."""
        s = self.state
        # Cancelar fade pendiente para que el skip sea inmediato
        s.transition_phase = ""
        s.transition_alpha = 0.0
        s.pending_room = ""
        rid = s.room_id
        s.paused = False
        s.hint_on = False
        s.selected_item = ""
        s.selected_verb = "Ir a"
        s.typing_buffer = ""

        def go(room: str, mode: str = "explore", feedback: str = "") -> None:
            s.goto(room, mode=mode, instant=True, clear_feedback=False, feedback=feedback)

        def say(msg: str) -> None:
            s.feedback = f"[DEBUG] {msg}"

        if rid == "splash":
            go("boot", feedback="[DEBUG] → boot")
        elif rid == "boot":
            go("ask_name", mode="type_name", feedback="[DEBUG] → perfil")
        elif rid in ("ask_name", "ask_vibe", "ask_handle"):
            if not s.player.name:
                s.player.name = "Tester"
            if not s.player.vibe:
                s.player.vibe = "arcade"
            if not s.player.handle:
                s.player.handle = "QA"
            go(
                "homebrew",
                feedback=f"[DEBUG] Perfil OK → Homebrew ({s.player.display_name})",
            )
        elif rid == "stack_puzzle":
            s.set_flag("has_grid_key")
            if "GRID-01" not in s.player.inventory:
                s.player.add_item("GRID-01")
            go("homebrew")
            say("STACK OK · GRID-01")
        elif rid == "modem":
            s.set_flag("has_grid_key")
            s.set_flag("key_inserted")
            s.set_flag("queue_ok")
            go("homebrew")
            say("QUEUE OK · portal listo")
        elif rid == "portal":
            s.set_flag("queue_ok")
            go("neon")
            say("→ Neon Calle")
        elif rid == "hash_puzzle":
            s.set_flag("neon_door_open")
            if s.credits < 5:
                s.credits = min(5, s.credits + 1)
            go("neon")
            say("HASH OK · Cantina abierta")
        elif rid == "homebrew":
            if not s.has("has_grid_key"):
                s.set_flag("has_grid_key")
                if "GRID-01" not in s.player.inventory:
                    s.player.add_item("GRID-01")
                say("STACK OK · GRID-01 (Ctrl+A otra vez)")
            elif not s.has("queue_ok"):
                s.set_flag("key_inserted")
                s.set_flag("queue_ok")
                say("QUEUE OK · portal listo (Ctrl+A → Neon)")
            else:
                go("neon")
                say("→ Neon Calle")
        elif rid == "neon":
            if not s.has("neon_door_open"):
                s.set_flag("neon_door_open")
                if s.credits < 5:
                    s.credits = min(5, s.credits + 1)
                say("HASH OK · Cantina abierta (Ctrl+A → Cantina)")
            else:
                go("cantina")
                say("→ Cantina · SET")
        elif rid == "cantina":
            if not s.has("set_ok"):
                for badge in ("SPOOF", "NULLPTR", "HALFAN", "GUEST99"):
                    if badge not in s.banned_ids:
                        s.banned_ids.append(badge)
                s.set_flag("set_ok")
                say("SET OK · Laberinto abierto (Ctrl+A → Maze)")
            else:
                s.maze_pos = 0
                go("maze", mode="puzzle")
                say("→ Laberinto · GRAFO")
        elif rid == "maze":
            s.maze_pos = 4
            s.set_flag("maze_ok")
            go("hal_ante")
            say("BFS OK → Antecámara HAL")
        elif rid == "hal_ante":
            if not s.has("hal_ok"):
                s.hal_step = 2
                s.set_flag("hal_ok")
                say("UNION-FIND OK · Cápsula lista (Ctrl+A → Acto II fin)")
            else:
                s.set_flag("act2_done")
                go("act2_end")
                say("→ Fin Acto II (Ctrl+A → Acto III)")
        elif rid in ("act2_end", "slice_end"):
            s.set_flag("act2_done")
            s.reset_act3_progress()
            if s.credits < 5:
                s.credits = min(5, s.credits + 1)
            go("evac_bay")
            say("→ Acto III · Bahía (Priority Queue)")
        elif rid == "evac_bay":
            if not s.has("heap_ok"):
                s.evac_step = 3
                s.set_flag("heap_ok")
                say("HEAP/PQ OK · Lab Prefijos (Ctrl+A → Trie)")
            else:
                s.trie_prefix = ""
                go("trie_lab", mode="puzzle")
                say("→ Lab · TRIE")
        elif rid == "trie_lab":
            if not s.has("trie_ok"):
                s.trie_prefix = "WOZ"
                s.set_flag("trie_ok")
                say("TRIE OK · Núcleo (Ctrl+A → Core)")
            else:
                s.core_step = 0
                go("hal_core", mode="puzzle")
                say("→ Núcleo · HEAP")
        elif rid == "hal_core":
            if not s.has("core_ok"):
                s.core_step = 3
                s.set_flag("core_ok")
                say("CORE OK · Cápsula (Ctrl+A → Ending)")
            else:
                s.set_flag("ending_seen")
                go("ending")
                say("→ Epílogo")
        elif rid in ("ending", "game_over_time"):
            say("Fin (Ctrl+Q salir / Reiniciar)")
        else:
            say(f"Sin skip para '{rid}'")

    def _on_motion(self, pos: tuple[int, int]) -> None:
        logic = self.renderer.screen_to_logical(*pos)
        if logic is None:
            self.state.hover_name = ""
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return
        lx, ly = logic
        view = self.current_view()
        clickable = False
        self.state.hover_name = ""

        if view.use_scumm:
            if view.back_room and back_button_rect().collidepoint(lx, ly):
                clickable = True
            for hit in verb_grid_rects():
                if hit.rect.collidepoint(lx, ly):
                    clickable = True
                    break
            if not clickable:
                for _, r in inventory_rects(self.state.player.inventory):
                    if r.collidepoint(lx, ly):
                        clickable = True
                        break
            if ly < config.scene_h(True):
                for hs in view.hotspots:
                    if hs.rect.collidepoint(lx, ly):
                        self.state.hover_name = hs.name
                        clickable = True
                        break
        else:
            for r in self.renderer.menu_option_rects:
                if r.collidepoint(lx, ly):
                    clickable = True
                    break

        pygame.mouse.set_cursor(
            pygame.SYSTEM_CURSOR_HAND if clickable else pygame.SYSTEM_CURSOR_ARROW
        )

    def _on_click(self, pos: tuple[int, int]) -> None:
        logic = self.renderer.screen_to_logical(*pos)
        if logic is None:
            return
        lx, ly = logic
        view = self.current_view()
        state = self.state

        if state.room_id == "splash":
            state.goto("boot", mode="explore")
            return

        if view.use_scumm:
            # Inventario antes que Volver (no deben solaparse; por si acaso)
            for hit in verb_grid_rects():
                if hit.rect.collidepoint(lx, ly):
                    state.selected_verb = hit.verb
                    if hit.verb not in ("Usar", "Dar"):
                        state.selected_item = ""
                    state.feedback = ""
                    return
            for item, r in inventory_rects(state.player.inventory):
                if r.collidepoint(lx, ly):
                    state.selected_item = item
                    if state.selected_verb not in ("Usar", "Dar"):
                        state.selected_verb = "Usar"
                    state.feedback = ""
                    return
            if view.back_room and back_button_rect().collidepoint(lx, ly):
                state.goto(view.back_room, mode=view.back_mode)
                return
            if ly < config.scene_h(True):
                for hs in view.hotspots:
                    if hs.rect.collidepoint(lx, ly):
                        state.feedback = ""
                        # Salidas de vuelta: un click alcanza (sin exigir verbo)
                        back_names = {
                            "Homebrew",
                            "Salida",
                            "Calle",
                            "Portal (vuelta)",
                        }
                        if (
                            hs.is_exit
                            and hs.name in back_names
                            and "Ir a" in hs.actions
                        ):
                            hs.actions["Ir a"](state)
                            return
                        self.world.try_verb_on(state, hs)
                        return
                # click vacío cierra el caption de diálogo
                state.feedback = ""
            return

        if state.mode not in ("type_name", "type_handle"):
            for i, r in enumerate(self.renderer.menu_option_rects):
                if r.collidepoint(lx, ly) and i < len(view.options):
                    state.feedback = ""
                    view.options[i].action(state)
                    return

    def _handle_typing(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            text = self.state.typing_buffer.strip()
            if self.state.mode == "type_name":
                if not text:
                    self.state.feedback = (
                        "PROTO-G: \"Un nombre, por favor. Aunque sea falso.\""
                    )
                    return
                self.state.player.name = text
                self.state.typing_buffer = ""
                self.state.goto("ask_vibe", mode="explore", clear_feedback=True)
            elif self.state.mode == "type_handle":
                self.state.player.handle = text
                self.state.typing_buffer = ""
                handle = self.state.player.display_name
                self.state.goto(
                    "homebrew",
                    mode="explore",
                    clear_feedback=True,
                    feedback=(
                        f"PROTO-G: \"Bienvenido, {handle}. "
                        "Verbo + objeto. Como antaño. "
                        "Si te trabás, pensá en Maniac… y en estaño.\""
                    ),
                )
                self.state.selected_verb = "Ir a"
            return
        if event.key == pygame.K_BACKSPACE:
            if (
                self.state.mode == "type_handle"
                and not self.state.typing_buffer
            ):
                self.state.goto("ask_vibe", mode="explore", clear_feedback=True)
                return
            if (
                self.state.mode == "type_name"
                and not self.state.typing_buffer
            ):
                self.state.goto("boot", mode="explore", clear_feedback=True)
                return
            self.state.typing_buffer = self.state.typing_buffer[:-1]
            return
        if event.key == pygame.K_ESCAPE:
            self.state.paused = True
            self.music.on_pause(True)
            return
        ch = event.unicode
        if ch and ch.isprintable() and len(self.state.typing_buffer) < 24 and ch != "\t":
            self.state.typing_buffer += ch

    def update(self, dt: float) -> None:
        self.state.update_transition(dt)
        rid = self.state.room_id
        if rid != self._music_room:
            self._music_room = rid
            self.music.update_for_room(rid)

    def draw(self, screen: pygame.Surface, width: int, height: int) -> None:
        self.renderer.draw(screen, self.current_view(), self.state, width, height)
