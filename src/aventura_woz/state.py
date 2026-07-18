"""Estado mutable de la partida."""

from dataclasses import dataclass, field

from aventura_woz import config
from aventura_woz.player import Player


@dataclass
class GameState:
    room_id: str = "splash"
    credits: int = config.START_CREDITS
    hint_on: bool = False
    feedback: str = ""
    paused: bool = False
    running: bool = True
    mode: str = "splash"
    player: Player = field(default_factory=Player)
    flags: dict[str, bool] = field(default_factory=dict)
    typing_buffer: str = ""
    selected_verb: str = "Ir a"
    hover_name: str = ""
    selected_item: str = ""
    # Acto II — progreso de puzzles
    banned_ids: list[str] = field(default_factory=list)
    maze_pos: int = 0
    hal_step: int = 0
    # Acto III
    evac_step: int = 0
    trie_prefix: str = ""
    core_step: int = 0
    # Transiciones
    transition_phase: str = ""  # "" | "out" | "in"
    transition_alpha: float = 0.0
    pending_room: str = ""
    pending_mode: str = "explore"
    pending_clear_feedback: bool = True
    pending_feedback: str = ""

    def spend_credit(self) -> None:
        self.credits = max(0, self.credits - 1)

    def reset_credits(self) -> None:
        self.credits = config.START_CREDITS

    def reset_act2_progress(self) -> None:
        self.banned_ids.clear()
        self.maze_pos = 0
        self.hal_step = 0
        for flag in (
            "neon_door_open",
            "set_ok",
            "maze_ok",
            "hal_ok",
            "act2_done",
        ):
            self.flags.pop(flag, None)

    def reset_act3_progress(self) -> None:
        self.evac_step = 0
        self.trie_prefix = ""
        self.core_step = 0
        for flag in (
            "heap_ok",
            "trie_ok",
            "core_ok",
            "ending_seen",
        ):
            self.flags.pop(flag, None)

    def _apply_goto(
        self, room_id: str, mode: str, clear_feedback: bool, feedback: str = ""
    ) -> None:
        self.room_id = room_id
        self.mode = mode
        self.hint_on = False
        self.typing_buffer = ""
        self.hover_name = ""
        if clear_feedback:
            self.feedback = feedback
        elif feedback:
            self.feedback = feedback

    def goto(
        self,
        room_id: str,
        mode: str = "explore",
        clear_feedback: bool = True,
        instant: bool = False,
        feedback: str = "",
    ) -> None:
        """Cambia de sala con fade (salvo instant o misma sala)."""
        if instant or room_id == self.room_id:
            self.transition_phase = ""
            self.transition_alpha = 0.0
            self._apply_goto(room_id, mode, clear_feedback, feedback)
            return
        # Si ya hay transición, aplica destino pendiente al toque
        self.pending_room = room_id
        self.pending_mode = mode
        self.pending_clear_feedback = clear_feedback
        self.pending_feedback = feedback
        if self.transition_phase != "out":
            self.transition_phase = "out"
            # no resetear alpha si ya estaba saliendo

    def update_transition(self, dt: float) -> None:
        if not self.transition_phase:
            return
        speed = config.TRANSITION_SPEED
        if self.transition_phase == "out":
            self.transition_alpha = min(255.0, self.transition_alpha + speed * dt)
            if self.transition_alpha >= 255.0:
                self._apply_goto(
                    self.pending_room,
                    self.pending_mode,
                    self.pending_clear_feedback,
                    self.pending_feedback,
                )
                self.pending_room = ""
                self.transition_phase = "in"
        elif self.transition_phase == "in":
            self.transition_alpha = max(0.0, self.transition_alpha - speed * dt)
            if self.transition_alpha <= 0.0:
                self.transition_phase = ""
                self.transition_alpha = 0.0

    @property
    def blocking_input(self) -> bool:
        return bool(self.transition_phase) or self.paused

    def set_flag(self, key: str, value: bool = True) -> None:
        self.flags[key] = value

    def has(self, key: str) -> bool:
        return bool(self.flags.get(key))

    @property
    def sentence(self) -> str:
        parts = [self.selected_verb]
        if self.selected_item and self.selected_verb in ("Usar", "Dar"):
            parts.append(self.selected_item)
            if self.hover_name:
                parts.append("con" if self.selected_verb == "Usar" else "a")
                parts.append(self.hover_name)
        elif self.hover_name:
            parts.append(self.hover_name)
        return " ".join(parts)
