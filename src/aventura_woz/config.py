"""Configuración — VGA-ish legible + layout SCUMM (Maniac Mansion)."""

# Ventana por defecto (intermedia; redimensionable)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
FPS = 60

# Resolución lógica (pixel art)
LOGICAL_W = 640
LOGICAL_H = 400

# Layout Maniac: escena grande; UI = sentence + verbos + status (sin hueco)
# verbos anclados al status; escena llega hasta la sentence
SCENE_H_SCUMM = 336
SCENE_H_MENU = 200
SENTENCE_H = 14
STATUS_H = 14
VERB_ROWS_H = 34  # 2 filas × 16 + margen
MENU_OPT_H = 16
MENU_OPT_MAX = 5

# Compat: altura de escena SCUMM por defecto
SCENE_H = SCENE_H_SCUMM


def scene_h(use_scumm: bool) -> int:
    return SCENE_H_SCUMM if use_scumm else SCENE_H_MENU


def sentence_y(use_scumm: bool) -> int:
    return scene_h(use_scumm) + 2


def ui_top(use_scumm: bool) -> int:
    return sentence_y(use_scumm) + SENTENCE_H


# Paleta EGA/CGA
BG = (0, 0, 0)
PHOSPHOR = (85, 255, 85)
PHOSPHOR_DIM = (0, 170, 0)
PHOSPHOR_DARK = (0, 85, 0)
CYAN = (85, 255, 255)
CYAN_DIM = (0, 170, 170)
MAGENTA = (255, 85, 255)
MAGENTA_DIM = (170, 0, 170)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 85)
RED = (255, 85, 85)
RED_DIM = (170, 0, 0)
BLUE = (85, 85, 255)
BLUE_DIM = (0, 0, 170)
GRAY = (170, 170, 170)
GRAY_DIM = (85, 85, 85)
PANEL_FILL = (0, 0, 40)
ORANGE = (255, 170, 85)

VERB_COLOR = PHOSPHOR
VERB_SELECTED = ORANGE
SENTENCE_COLOR = MAGENTA
INV_COLOR = MAGENTA

FONT_FAMILY = "consolas"
FONT_SIZE = 14
FONT_SIZE_TITLE = 18
FONT_SIZE_SMALL = 12
FONT_SIZE_VERB = 12

START_CREDITS = 3
SCANLINE_ALPHA = 28

# Música (0.0–1.0); M mutea in-game
MUSIC_VOLUME = 0.35

# Transiciones (fade a negro)
TRANSITION_SPEED = 520.0  # alpha por segundo

VERBS = [
    "Ir a",
    "Mirar",
    "Agarrar",
    "Hablar",
    "Usar",
    "Abrir",
    "Cerrar",
    "Empujar",
    "Tirar",
    "Dar",
]

VERB_COLS = 5
VERB_ROWS = 2
