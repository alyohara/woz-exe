"""Música de fondo WOZ.exe — loops por acto; mute con M."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import pygame

from aventura_woz import config

_AUDIO_DIR = Path(__file__).resolve().parent / "audio"

# room_id → stem del archivo (sin extensión)
_TRACK_FOR_ROOM: dict[str, str] = {
    "splash": "theme_boot",
    "boot": "theme_boot",
    "ask_name": "theme_boot",
    "ask_vibe": "theme_boot",
    "ask_handle": "theme_boot",
    "homebrew": "theme_act1",
    "stack_puzzle": "theme_act1",
    "modem": "theme_act1",
    "portal": "theme_act1",
    "neon": "theme_act2",
    "hash_puzzle": "theme_act2",
    "cantina": "theme_act2",
    "maze": "theme_act2",
    "hal_ante": "theme_act2",
    "act2_end": "theme_act2",
    "slice_end": "theme_act2",
    "evac_bay": "theme_act3",
    "trie_lab": "theme_act3",
    "hal_core": "theme_act3",
    "ending": "theme_ending",
    "game_over_time": "theme_gameover",
}

# Parámetros de melodías procedurales (Hz relativos, estilo chiptune)
_MELODIES: dict[str, tuple[list[float], float, float]] = {
    # (notas en Hz, bpm-ish step, volumen pico 0-1)
    "theme_boot": (
        [196, 0, 220, 0, 247, 0, 262, 0, 247, 0, 220, 0],
        0.22,
        0.18,
    ),
    "theme_act1": (
        [262, 294, 330, 294, 262, 0, 196, 220, 262, 0],
        0.18,
        0.16,
    ),
    "theme_act2": (
        [330, 0, 311, 330, 370, 0, 349, 330, 294, 0],
        0.16,
        0.15,
    ),
    "theme_act3": (
        [147, 175, 196, 0, 185, 196, 220, 0, 147, 0],
        0.20,
        0.17,
    ),
    "theme_ending": (
        [262, 330, 392, 330, 349, 392, 523, 0],
        0.24,
        0.16,
    ),
    "theme_gameover": (
        [220, 208, 196, 185, 175, 0, 147, 0],
        0.28,
        0.14,
    ),
}


def _ensure_track(stem: str) -> Path | None:
    """Devuelve path .wav/.ogg/.mp3 si existe; si no, genera chiptune .wav."""
    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for ext in (".ogg", ".mp3", ".wav"):
        path = _AUDIO_DIR / f"{stem}{ext}"
        if path.exists():
            return path
    if stem not in _MELODIES:
        return None
    path = _AUDIO_DIR / f"{stem}.wav"
    if not path.exists():
        _write_chiptune(path, *_MELODIES[stem])
    return path


def _write_chiptune(
    path: Path, notes: list[float], note_len: float, volume: float
) -> None:
    """Loop corto square-wave (estilo DOS / chiptune)."""
    sample_rate = 22050
    frames: list[int] = []
    for freq in notes:
        n = int(sample_rate * note_len)
        for i in range(n):
            if freq <= 0:
                sample = 0
            else:
                t = i / sample_rate
                # square + leve decay por nota
                amp = volume * (1.0 - 0.35 * (i / max(n, 1)))
                sample = amp if math.sin(2 * math.pi * freq * t) >= 0 else -amp
            frames.append(int(max(-1.0, min(1.0, sample)) * 32000))
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(struct.pack("<h", f) for f in frames))


class MusicPlayer:
    """Cambia de tema según la sala; M mutea."""

    def __init__(self) -> None:
        self.enabled = True
        self.muted = False
        self._current = ""
        self._ready = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
            self._ready = True
        except pygame.error:
            self._ready = False

    def update_for_room(self, room_id: str) -> None:
        if not self._ready or self.muted:
            return
        stem = _TRACK_FOR_ROOM.get(room_id, "theme_act1")
        if stem == self._current and pygame.mixer.music.get_busy():
            return
        path = _ensure_track(stem)
        if path is None:
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(
                0.0 if self.muted else config.MUSIC_VOLUME
            )
            self._current = stem
        except pygame.error:
            self._current = ""

    def toggle_mute(self) -> str:
        if not self._ready:
            return "Sin audio disponible."
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.music.set_volume(0.0)
            return "Música: OFF (M para activar)"
        pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
        if not pygame.mixer.music.get_busy() and self._current:
            path = _ensure_track(self._current)
            if path:
                try:
                    pygame.mixer.music.load(str(path))
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    pass
        return "Música: ON"

    def on_pause(self, paused: bool) -> None:
        if not self._ready or self.muted:
            return
        if paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def stop(self) -> None:
        if self._ready:
            pygame.mixer.music.stop()
        self._current = ""
