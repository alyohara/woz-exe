"""Mundo SCUMM: hotspots clickeables + puzzles embebidos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame

from aventura_woz import scenes
from aventura_woz.player import Player, VIBES
from aventura_woz.scumm import Hotspot, default_response
from aventura_woz.state import GameState


ActionFn = Callable[[GameState], None]


@dataclass
class Option:
    label: str
    action: ActionFn


@dataclass
class RoomView:
    room_id: str
    title: str
    narration: str
    hint: str
    options: list[Option] = field(default_factory=list)
    hotspots: list[Hotspot] = field(default_factory=list)
    draw_art: Callable[[pygame.Surface, pygame.Rect, GameState], None] | None = None
    use_scumm: bool = False  # True = UI de verbos + click en escena
    back_room: str | None = None  # sala padre para botón Volver
    back_mode: str = "explore"


def _fail(state: GameState, message: str) -> None:
    state.spend_credit()
    state.feedback = message
    state.hint_on = False
    if state.credits <= 0:
        state.goto("game_over_time", clear_feedback=False)


def _say(state: GameState, message: str) -> None:
    state.feedback = message


def _reboot_to_splash(state: GameState) -> None:
    state.player = Player()
    state.flags.clear()
    state.reset_act2_progress()
    state.reset_act3_progress()
    state.reset_credits()
    state.selected_verb = "Ir a"
    state.selected_item = ""
    state.goto("splash", mode="splash")


_PUZZLE_FLAGS_ACT1 = (
    "has_grid_key",
    "key_inserted",
    "queue_ok",
    "neon_door_open",
    "read_boot_msg",
    "read_woz_note",
)

# Impostores a banear en la Cantina (SET). WOZ no se toca.
_SET_IMPOSTORS = ("SPOOF", "NULLPTR", "HALFAN", "GUEST99")

# Grafo del laberinto (arte): camino 0→1→3→4; nodo 2 = foso sin aristas
_MAZE_EDGES: dict[int, list[int]] = {
    0: [1],
    1: [0, 3],
    2: [],
    3: [1, 4],
    4: [],
}
_MAZE_LABELS = {
    0: "Nodo 0 (inicio)",
    1: "Nodo 1",
    2: "Nodo 2 (foso)",
    3: "Nodo 3",
    4: "Nodo 4 (salida)",
}

# Acto III — Priority Queue: extract-min por prioridad 1→2→3
_EVAC_ORDER = ("P1 WOZ", "P2 CREW", "P3 CARGO")

# Trie: camino correcto W→O→Z
_TRIE_TARGET = "WOZ"

# Núcleo HAL — apagar por prioridad (heap extract-min)
_CORE_ORDER = ("MEMORY", "LOGIC", "EYE")


def _enter_act3(state: GameState) -> None:
    state.set_flag("act2_done")
    state.reset_act3_progress()
    if state.credits < 5:
        state.credits = min(5, state.credits + 1)
    state.goto(
        "evac_bay",
        clear_feedback=False,
        feedback=(
            f'HAL: "Welcome to the core, {state.player.name}."\n'
            'CAP. QUEUE: "Prioridad primero. WOZ sale antes que el café."\n'
            "[ACTO III]"
        ),
    )


def _retry_puzzles(state: GameState) -> None:
    """Retry: mantiene perfil; reinicia puzzles Acto I + II + III."""
    for flag in _PUZZLE_FLAGS_ACT1:
        state.flags.pop(flag, None)
    state.reset_act2_progress()
    state.reset_act3_progress()
    state.player.inventory = [
        item for item in state.player.inventory if item != "GRID-01"
    ]
    state.selected_item = ""
    state.selected_verb = "Ir a"
    state.reset_credits()
    state.goto(
        "homebrew",
        feedback=(
            'PROTO-G: "Otra vez. Misma pila, misma cola, mismo heap. '
            'Como el continue del arcade… pero con dignidad."'
        ),
    )


class World:
    def view(self, state: GameState) -> RoomView:
        rid = state.room_id
        builders = {
            "splash": self._splash,
            "boot": self._boot,
            "ask_name": self._ask_name,
            "ask_vibe": self._ask_vibe,
            "ask_handle": self._ask_handle,
            "homebrew": self._homebrew,
            "stack_puzzle": self._stack_puzzle,
            "modem": self._modem,
            "portal": self._portal,
            "neon": self._neon,
            "hash_puzzle": self._hash_puzzle,
            "cantina": self._cantina,
            "maze": self._maze,
            "hal_ante": self._hal_ante,
            "act2_end": self._act2_end,
            "slice_end": self._act2_end,
            "evac_bay": self._evac_bay,
            "trie_lab": self._trie_lab,
            "hal_core": self._hal_core,
            "ending": self._ending,
            "game_over_time": self._game_over,
        }
        return builders.get(rid, self._splash)(state)

    def try_verb_on(self, state: GameState, hotspot: Hotspot) -> None:
        verb = state.selected_verb
        # Use item with object
        if verb == "Usar" and state.selected_item:
            key = f"Usar:{state.selected_item}"
            if key in hotspot.actions:
                hotspot.actions[key](state)
                state.selected_item = ""
                return
            _say(state, f"No tiene sentido usar {state.selected_item} con {hotspot.name}.")
            return
        if verb in hotspot.actions:
            hotspot.actions[verb](state)
            return
        if verb == "Ir a" and hotspot.is_exit and "Ir a" in hotspot.actions:
            hotspot.actions["Ir a"](state)
            return
        _say(state, default_response(verb, hotspot.name))

    def _splash(self, state: GameState) -> RoomView:
        return RoomView(
            "splash",
            "PRESENTA",
            "Leonardo Bianco presenta\n"
            "inspirado en la programación de Flavio Speche\n\n"
            "WOZ.exe\n\n"
            "Hacé click en la escena o pulsá ENTER para continuar.",
            "Una aventura point-and-click de estructuras de datos.",
            options=[
                Option("Continuar", lambda s: s.goto("boot", mode="explore")),
            ],
            draw_art=scenes.draw_splash,
            use_scumm=False,
        )

    def _boot(self, state: GameState) -> RoomView:
        return RoomView(
            "boot",
            "ARRANQUE",
            "Un Apple II olvidado parpadea:\n\n    FIND WOZ. HAL KNOWS.\n\n"
            "Alguien — o algo — está esperando.\n"
            "Antes de entrar, el sistema quiere saber quién sos.",
            "Arrancá el sistema.",
            options=[
                Option("Arrancar sistema", lambda s: s.goto("ask_name", mode="type_name")),
                Option(
                    "Leer créditos",
                    lambda s: _say(
                        s,
                        "WOZ.exe — aventura de estructuras de datos\n"
                        "Inspirada en Maniac Mansion y la CF de los 80/90.\n"
                        "\"I'm afraid this is only the beginning.\" — H.",
                    ),
                ),
                Option("Salir a DOS", lambda s: setattr(s, "running", False)),
            ],
            draw_art=scenes.draw_boot,
        )

    def _ask_name(self, state: GameState) -> RoomView:
        return RoomView(
            "ask_name",
            "PERFIL · NOMBRE",
            "PROTO-G: \"Identificate, Usuario.\n"
            "          Escribí tu nombre y pulsá ENTER.\"\n\n"
            f"    NOMBRE> {state.typing_buffer}_",
            "Escribí tu nombre.",
            options=[Option("(Teclado + ENTER)", lambda s: None)],
            draw_art=scenes.draw_profile,
        )

    def _ask_vibe(self, state: GameState) -> RoomView:
        name = state.player.name

        def set_vibe(key: str) -> ActionFn:
            def _act(s: GameState) -> None:
                s.player.vibe = key
                s.goto("ask_handle", mode="type_handle")
                _say(
                    s,
                    f"PROTO-G: \"{VIBES[key]['short']} — anotado, {name}.\n"
                    "          ¿Un handle? Escribilo, o ENTER vacío para seguir.\"",
                )

            return _act

        return RoomView(
            "ask_vibe",
            "PERFIL · CÓMO SOS",
            f"PROTO-G: \"Gusto en conocerte, {name}.\n"
            "          ¿Cómo laburás? Elegí un estilo.\"",
            "Elegí cómo sos.",
            options=[
                Option(
                    "← Cambiar nombre",
                    lambda s: s.goto("ask_name", mode="type_name"),
                ),
            ]
            + [Option(VIBES[k]["label"], set_vibe(k)) for k in VIBES],
            draw_art=scenes.draw_profile,
        )

    def _ask_handle(self, state: GameState) -> RoomView:
        return RoomView(
            "ask_handle",
            "PERFIL · HANDLE",
            f"Nombre: {state.player.name}   Estilo: {state.player.vibe_short}\n\n"
            "PROTO-G: \"Un handle ayuda en Neon Calle.\n"
            "          Escribí uno + ENTER (vacío = solo tu nombre).\"\n\n"
            f"    HANDLE> {state.typing_buffer}_",
            "Handle opcional.",
            options=[Option("(Teclado + ENTER)", lambda s: None)],
            draw_art=scenes.draw_profile,
        )

    def _homebrew(self, state: GameState) -> RoomView:
        name = state.player.display_name
        r = scenes.homebrew_rects()
        spots: list[Hotspot] = [
            Hotspot(
                "Apple II",
                r["Apple II"],
                {
                    "Mirar": lambda s: (
                        s.set_flag("read_boot_msg"),
                        _say(
                            s,
                            "El Apple II parpadea: FIND WOZ. HAL KNOWS.\n"
                            "Parece un mensaje de WarGames… pero con peor ortografía cósmica.",
                        ),
                    ),
                    "Usar": lambda s: _say(
                        s, "Ya está arrancado. No hace falta soplarle como al NES."
                    ),
                    "Abrir": lambda s: _say(
                        s, "La carcasa está soldada con amor. Y estaño. Mucho estaño."
                    ),
                },
            ),
            Hotspot(
                "Banco",
                r["Banco"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Una PILA de placas. La de arriba brilla dorada.\n"
                        "Vibes LIFO. Como la bandeja de entrada… o el último disco de Queen en el stereo.",
                    ),
                    "Usar": lambda s: s.goto("stack_puzzle", mode="puzzle")
                    if not s.has("has_grid_key")
                    else _say(s, "La pila ya entregó la DORADA. No hay secuela. Todavía."),
                    "Agarrar": lambda s: s.goto("stack_puzzle", mode="puzzle")
                    if not s.has("has_grid_key")
                    else _say(s, "Ya tenés la tarjeta DORADA. Relajá, Indiana."),
                    "Empujar": lambda s: _say(
                        s, "La mesa no se mueve. Woz la atornilló. Nivel Terminator: unstoppable."
                    ),
                },
            ),
            Hotspot(
                "Nota",
                r["Nota"],
                {
                    "Mirar": lambda s: (
                        s.set_flag("read_woz_note"),
                        _say(
                            s,
                            "Nota de Woz: \"Si leés esto: LIFO. Lo último es la llave.\"\n"
                            "Firmado como si fuera un post-it de X-Files. Quiero creer.",
                        ),
                    ),
                    "Agarrar": lambda s: _say(
                        s, "Mejor dejarla: es pista, no loot. Esto no es Diablo."
                    ),
                },
            ),
            Hotspot(
                "Herramientas",
                r["Herramientas"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Estaño, flux, un integrado sin patas. Taller de garage, vibe MacGyver."
                        + (
                            f" Como chico del garage, {s.player.name}, husmeás: Woz estuvo acá."
                            if s.player.vibe == "garage"
                            else ""
                        ),
                    ),
                    "Agarrar": lambda s: _say(
                        s, "PROTO-G: \"Ese soldador no es tuyo. Ni el de Doc Brown.\""
                    ),
                },
            ),
            Hotspot(
                "Módem",
                r["Módem"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "300 baud. INSERT KEY / GRID-01.\n"
                        "Suena como el fax de tu tío en 1992… pero con más destiny.",
                    ),
                    "Ir a": lambda s: s.goto("modem"),
                    "Usar": lambda s: s.goto("modem"),
                    "Hablar": lambda s: _say(
                        s, "El módem solo habla en chirridos. Es el dial-up de Matrix, edición museo."
                    ),
                },
                is_exit=True,
            ),
            Hotspot(
                "Portal",
                r["Portal"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Un arco de luz. Esto parece sacado de Tron… o de un lavarropas poseído."
                        + (" ¡CARRIER DETECT!" if s.has("queue_ok") else " Incompleto."),
                    ),
                    "Ir a": lambda s: s.goto("portal"),
                    "Usar": lambda s: s.goto("portal"),
                    "Abrir": lambda s: _say(
                        s, "No es una puerta. Es un portal. Andá hacia él. Como en Stargate, pero más pixel."
                    ),
                },
                is_exit=True,
            ),
            Hotspot(
                "Ventana",
                r["Ventana"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Neon lejano: LORA NEON. Blade Runner de barrio.\n"
                        "Primero, el portal. Después el ramen.",
                    ),
                    "Abrir": lambda s: _say(
                        s, "Trancada. Clásico. Ni con la ganzúa de Solid Snake."
                    ),
                },
            ),
            Hotspot(
                "PROTO-G",
                r["PROTO-G"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Un guía glitchy. Mitad droid, mitad screensaver de After Dark.\n"
                        "Si habla raro, es feature, no bug.",
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        f"PROTO-G: \"{name}: pila en el banco, módem FIFO, "
                        "portal cuando ambos canten.\"\n"
                        "PROTO-G: \"Sí, es como Maniac Mansion… pero con más estaño.\"",
                    ),
                    "Dar": lambda s: _say(
                        s, "PROTO-G no acepta sobornos. Solo data. Y memes de 1994, máximo."
                    ),
                },
            ),
        ]

        extra = ""
        if state.has("has_grid_key"):
            extra += "\nInventario: tarjeta DORADA (GRID-01)."
        if state.has("queue_ok"):
            extra += "\nEl portal zumba: CARRIER DETECT."

        return RoomView(
            "homebrew",
            "TALLER HOMEBREW",
            f"Taller Homebrew. Huele a estaño y a nostalgia cara.\n"
            f"PROTO-G: \"Señalá, click, verbo — como antaño, {name}. "
            "Maniac vibes, zero royalties.\"\n"
            f"{extra}",
            "Mirar Nota · Usar/Agarrar Banco · Ir a Módem/Portal",
            hotspots=spots,
            draw_art=scenes.draw_homebrew,
            use_scumm=True,
        )

    def _stack_puzzle(self, state: GameState) -> RoomView:
        def pop_ok(s: GameState) -> None:
            s.set_flag("has_grid_key")
            s.player.add_item("GRID-01")
            s.goto("homebrew", clear_feedback=False)
            _say(
                s,
                "Agarrar / Usar TOPE → tarjeta DORADA (GRID-01)!\n"
                f"PROTO-G: \"Llave adquirida, {s.player.display_name}. "
                "Andá al módem y Usá GRID-01.\"\n"
                "Suena a power-up de arcade. Insert coin… de estaño.",
            )

        r = scenes.stack_rects()
        spots = [
            Hotspot(
                "Tarjeta TOPE",
                r["Tarjeta TOPE"],
                {
                    "Mirar": lambda s: _say(
                        s, "DORADA. El tope de la pila. LIFO!\nComo el último VHS arriba del tele."
                    ),
                    "Agarrar": pop_ok,
                    "Usar": pop_ok,
                    "Empujar": lambda s: _fail(
                        s,
                        "PUSH basura… el tope miente.\nTIME CREDIT -1\n"
                        f"HAL: \"Not optimal, {s.player.name}.\"\n"
                        "(HAL no entiende el humor. Típico villano 2001.)",
                    ),
                },
            ),
            Hotspot(
                "Base de la pila",
                r["Base de la pila"],
                {
                    "Mirar": lambda s: _say(
                        s, "ROJO en la base. El secreto no está abajo.\n"
                        "Spoiler: nunca está abajo. Excepto en Alien."
                    ),
                    "Agarrar": lambda s: _say(
                        s, "Tendrías que sacar primero lo de arriba. LIFO.\n"
                        "O sea: no seas el tipo que saca el disco de abajo de la torre."
                    ),
                },
            ),
            Hotspot(
                "Salida",
                r["Salida"],
                {
                    "Ir a": lambda s: s.goto("homebrew"),
                    "Mirar": lambda s: _say(s, "Volver al taller. Exit stage left."),
                },
                is_exit=True,
            ),
        ]
        return RoomView(
            "stack_puzzle",
            "BANCO · PILA",
            "Pila de placas. LIFO.\nAgarrá / Usá la tarjeta del TOPE.",
            "Agarrá el TOPE (DORADA).",
            hotspots=spots,
            draw_art=scenes.draw_stack,
            use_scumm=True,
            back_room="homebrew",
        )

    def _modem(self, state: GameState) -> RoomView:
        mr = scenes.modem_rects()
        if state.has("queue_ok"):
            return RoomView(
                "modem",
                "MÓDEM",
                "CARRIER DETECT. Cola completa.",
                "Andá al Portal o al Homebrew.",
                hotspots=[
                    Hotspot(
                        "Homebrew",
                        mr["Homebrew"],
                        {"Ir a": lambda s: s.goto("homebrew")},
                        is_exit=True,
                    ),
                    Hotspot(
                        "Portal",
                        mr["Portal"],
                        {"Ir a": lambda s: s.goto("portal")},
                        is_exit=True,
                    ),
                ],
                draw_art=scenes.draw_modem,
                use_scumm=True,
                back_room="homebrew",
            )

        if not state.has("has_grid_key"):
            return RoomView(
                "modem",
                "MÓDEM",
                "Parpadea: INSERT KEY / GRID-01",
                "Volvé al banco (STACK).",
                hotspots=[
                    Hotspot(
                        "Modem",
                        mr["Modem"],
                        {
                            "Mirar": lambda s: _say(
                                s,
                                "Tono ocupado. Necesitás la tarjeta GRID-01.\n"
                                "Sin llave sos el tipo de Terminator sin moto. Triste.",
                            ),
                            "Usar": lambda s: _say(
                                s,
                                "PROTO-G: \"Primero la pila (STACK). Después FIFO.\"\n"
                                "PROTO-G: \"Orden, padawan… digo, usuario.\"",
                            ),
                        },
                    ),
                    Hotspot(
                        "Homebrew",
                        mr["Homebrew"],
                        {"Ir a": lambda s: s.goto("homebrew")},
                        is_exit=True,
                    ),
                ],
                draw_art=scenes.draw_modem,
                use_scumm=True,
                back_room="homebrew",
            )

        def insert_key(s: GameState) -> None:
            s.set_flag("key_inserted")
            s.selected_item = ""
            _say(
                s,
                "GRID-01 click. Insertada. Como el cassette en el Walkman… pero con destiny.\n"
                "Cola FIFO lista: FIND → WOZ → HAL-KNOWS.",
            )

        if not state.has("key_inserted"):
            return RoomView(
                "modem",
                "MÓDEM",
                "Slot abierto. Seleccioná GRID-01 en Inventario,\n"
                "verbo Usar, después el módem.",
                "Usar GRID-01 con el módem.",
                hotspots=[
                    Hotspot(
                        "Modem",
                        mr["Modem"],
                        {
                            "Mirar": lambda s: _say(
                                s, "Hay un slot GRID-01. La llave está en tu inventario."
                            ),
                            "Usar:GRID-01": insert_key,
                            "Usar": lambda s: _say(
                                s,
                                "PROTO-G: \"Seleccioná GRID-01 (inventario) y Usá el módem.\"",
                            )
                            if not s.selected_item
                            else _say(s, f"No encaja {s.selected_item} acá."),
                        },
                    ),
                    Hotspot(
                        "Homebrew",
                        mr["Homebrew"],
                        {"Ir a": lambda s: s.goto("homebrew")},
                        is_exit=True,
                    ),
                ],
                draw_art=scenes.draw_modem,
                use_scumm=True,
                back_room="homebrew",
            )

        def enqueue_ok(s: GameState) -> None:
            s.set_flag("queue_ok")
            s.goto("homebrew", clear_feedback=False)
            _say(
                s,
                "QUEUE: FIND · WOZ · HAL-KNOWS\nModem: CARRIER DETECT\n"
                f"PROTO-G: \"Portal en vivo, {s.player.display_name}.\"\n"
                "Suena el módem como si Outside estuviera por empezar. (No empieza.)",
            )

        return RoomView(
            "modem",
            "MÓDEM · COLA",
            "GRID-01 insertada. Encolá FIFO: FIND → WOZ → HAL-KNOWS\n"
            "Usá la cola en el orden correcto.",
            "Usá Cola correcta.",
            hotspots=[
                Hotspot(
                    "Cola correcta",
                    mr["Cola correcta"],
                    {
                        "Mirar": lambda s: _say(
                            s, "Slots listos: FIND, WOZ, HAL-KNOWS."
                        ),
                        "Usar": enqueue_ok,
                        "Empujar": enqueue_ok,
                    },
                ),
                Hotspot(
                    "Orden incorrecto",
                    mr["Orden incorrecto"],
                    {
                        "Usar": lambda s: _fail(
                            s,
                            "Mensaje corrupto.\nTIME CREDIT -1\n"
                            f"HAL: \"I'm sorry, {s.player.name}.\"",
                        ),
                        "Mirar": lambda s: _say(s, "Ese orden huele mal. HAL knows."),
                    },
                ),
                Hotspot(
                    "Homebrew",
                    mr["Homebrew"],
                    {"Ir a": lambda s: s.goto("homebrew")},
                    is_exit=True,
                ),
            ],
            draw_art=scenes.draw_modem,
            use_scumm=True,
            back_room="homebrew",
        )

    def _portal(self, state: GameState) -> RoomView:
        name = state.player.name or "Usuario"
        pr = scenes.portal_rects()
        if not state.has("queue_ok"):
            return RoomView(
                "portal",
                "PORTAL",
                f"Arco incompleto.\nVoz: \"Not yet, {name}.\"",
                "Completá STACK + QUEUE.",
                hotspots=[
                    Hotspot(
                        "Homebrew",
                        pr["Homebrew"],
                        {"Ir a": lambda s: s.goto("homebrew")},
                        is_exit=True,
                    ),
                    Hotspot(
                        "Portal",
                        pr["Portal"],
                        {
                            "Mirar": lambda s: _say(
                                s, "Líneas cian a medias. Stargate en modo demo."
                            ),
                            "Ir a": lambda s: _say(
                                s,
                                "Te atraviesa un escalofrío. Nada.\n"
                                "Como cruzar la puerta del club sin estar en la lista.",
                            ),
                            "Usar": lambda s: _say(
                                s, "HAL: \"Insurance takes time.\" (No es un chiste. Él no hace chistes.)"
                            ),
                        },
                    ),
                ],
                draw_art=scenes.draw_portal,
                use_scumm=True,
                back_room="homebrew",
            )

        return RoomView(
            "portal",
            "UMBRAL DEL PORTAL",
            f"\"Good evening, {name}. I am… insurance.\"\n"
            "PROTO-G: \"Eso no suena amistoso. Suena a villano de los 90 con presupuesto.\"",
            "Andá al Portal para entrar a Neon Calle.",
            hotspots=[
                Hotspot(
                    "Portal",
                    pr["Portal"],
                    {
                        "Ir a": lambda s: s.goto("neon"),
                        "Usar": lambda s: s.goto("neon"),
                        "Mirar": lambda s: _say(
                            s,
                            "Grid infinito. Light-cycles. Ojos rojos.\n"
                            "Tron se cruzó con 2001 y nadie salió ileso.",
                        ),
                        "Hablar": lambda s: _say(
                            s,
                            f"HAL: \"Good evening, {name}.\"\n"
                            "(No digas ‘open the pod bay doors’. No funciona.)",
                        ),
                    },
                    is_exit=True,
                ),
                Hotspot(
                    "Homebrew",
                    pr["Homebrew"],
                    {"Ir a": lambda s: s.goto("homebrew")},
                    is_exit=True,
                ),
            ],
            draw_art=scenes.draw_portal,
            use_scumm=True,
            back_room="homebrew",
        )

    def _neon(self, state: GameState) -> RoomView:
        handle = state.player.display_name
        nr = scenes.neon_rects()
        hotspots = [
            Hotspot(
                "Puerta de acero",
                nr["Puerta de acero"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Buckets [0]..[6]. hash = sum(ord) mod 7. Clave WOZ?\n"
                        "Parece el teclado de un bunker de WarGames. Menos NORAD, más neon.",
                    ),
                    "Ir a": lambda s: s.goto("hash_puzzle", mode="puzzle"),
                    "Usar": lambda s: s.goto("hash_puzzle", mode="puzzle"),
                    "Abrir": lambda s: s.goto("hash_puzzle", mode="puzzle"),
                },
                is_exit=True,
            ),
            Hotspot(
                "Lora",
                nr["Lora"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Vapor de fósforo. Actitud Neon.\n"
                        "Si esto fuera Blade Runner, ella ya te habría testeado.",
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        (
                            f'LORA: "La puerta HASH ya cedió, {handle}. '
                            'La Cantina es el SET de los IDs. Banear impostores."\n'
                            'LORA: "Y si ves un laberinto… BFS, no intuición de arcade."'
                            if s.has("neon_door_open")
                            else (
                                f'LORA: "Acá las puertas abren por HASH, {handle}.\n'
                                '       La puerta HASH. No te mueras."\n'
                                "LORA: \"Y si ves un ojo rojo… no le digas "
                                "'I'll be back'.\""
                            )
                        ),
                    ),
                },
            ),
            Hotspot(
                "Portal (vuelta)",
                nr["Portal (vuelta)"],
                {"Ir a": lambda s: s.goto("portal")},
                is_exit=True,
            ),
        ]
        if state.has("neon_door_open"):
            hotspots.insert(
                0,
                Hotspot(
                    "Cantina",
                    nr["Cantina"],
                    {
                        "Mirar": lambda s: _say(
                            s,
                            "Neón naranja. Humo. Badges de IDs flotando.\n"
                            "Huele a SET: sin duplicados, con drama.",
                        ),
                        "Ir a": lambda s: s.goto("cantina"),
                        "Usar": lambda s: s.goto("cantina"),
                        "Abrir": lambda s: s.goto("cantina"),
                    },
                    is_exit=True,
                ),
            )
        narr = (
            f"La puerta HASH está abierta. Un callejón lleva a la Cantina.\n"
            f'Lora: "Bienvenido al Acto II, {handle}. Filtrá el SET."'
            if state.has("neon_door_open")
            else (
                f"Lluvia sintética. Huele a cable quemado y a futuro que prometió volar autos.\n"
                f'Lora: "Así que sos {handle}. Mirá alrededor."'
            )
        )
        return RoomView(
            "neon",
            "CALLE NEÓN",
            narr,
            (
                "Andá a la Cantina · o volvé a la puerta HASH"
                if state.has("neon_door_open")
                else "Hablá con Lora · Usá/Andá a la puerta"
            ),
            hotspots=hotspots,
            draw_art=scenes.draw_neon,
            use_scumm=True,
            back_room="portal",
        )

    def _hash_puzzle(self, state: GameState) -> RoomView:
        def ok(s: GameState) -> None:
            first = not s.has("neon_door_open")
            s.set_flag("neon_door_open")
            if first and s.credits < 5:
                s.credits = min(5, s.credits + 1)
            s.goto("neon", clear_feedback=False)
            _say(
                s,
                "hash(\"WOZ\") → bucket 4. CLICK!\n"
                f'LORA: "Nada mal, {s.player.display_name}. Eso fue… casi elegante."\n'
                f'HAL: "Very well, {s.player.name}. Unfortunate."\n'
                "El callejón a la Cantina se ilumina. (Acto II.)",
            )

        spots = []
        for i, rect in enumerate(scenes.hash_bucket_rects()):

            def make_use(bucket: int) -> ActionFn:
                def _act(s: GameState) -> None:
                    if bucket == 4:
                        ok(s)
                    else:
                        _fail(
                            s,
                            f"Bucket {bucket} incorrecto.\nTIME CREDIT -1\n"
                            'LORA: "Colisión con la estupidez. Clásico hash fail."\n'
                            f'HAL: "I\'m sorry, {s.player.name}."',
                        )

                return _act

            spots.append(
                Hotspot(
                    f"Bucket {i}",
                    rect,
                    {
                        "Mirar": lambda s, b=i: _say(s, f"Bucket {b}."),
                        "Usar": make_use(i),
                        "Empujar": make_use(i),
                        "Ir a": make_use(i),
                    },
                )
            )
        spots.append(
            Hotspot(
                "Calle",
                scenes.hash_exit_rect(),
                {"Ir a": lambda s: s.goto("neon")},
                is_exit=True,
            )
        )
        return RoomView(
            "hash_puzzle",
            "PUERTA · HASH",
            'hash("WOZ") = sum(ord) mod 7\nUsá / Andá al bucket correcto.',
            "Bucket 4. (87+79+90)%7 = 4",
            hotspots=spots,
            draw_art=scenes.draw_hash,
            use_scumm=True,
            back_room="neon",
        )

    def _cantina(self, state: GameState) -> RoomView:
        """Hub SET: banear impostores; dejar WOZ."""
        cr = scenes.cantina_rects()
        banned = set(state.banned_ids)
        left = [x for x in _SET_IMPOSTORS if x not in banned]

        def ban_id(badge: str) -> ActionFn:
            def _act(s: GameState) -> None:
                if badge == "WOZ":
                    _fail(
                        s,
                        "Banear WOZ? Eso es… el opuesto de rescatar.\n"
                        "TIME CREDIT -1\n"
                        f'HAL: "Thank you for the assistance, {s.player.name}."',
                    )
                    return
                if badge in s.banned_ids:
                    _say(s, f"{badge} ya está fuera del SET.")
                    return
                s.banned_ids.append(badge)
                remaining = [x for x in _SET_IMPOSTORS if x not in s.banned_ids]
                if remaining:
                    _say(
                        s,
                        f"REMOVE {badge}. SET −1.\n"
                        f"Impostores restantes: {', '.join(remaining)}",
                    )
                else:
                    s.set_flag("set_ok")
                    _say(
                        s,
                        "SET limpio. Solo queda WOZ.\n"
                        'BARTENDER-BOT: "Unique. No duplicates. Nice."\n'
                        "Se abre el pasaje al Laberinto de Nodos.",
                    )

            return _act

        hotspots: list[Hotspot] = []
        for badge in (*_SET_IMPOSTORS, "WOZ"):
            if badge in banned and badge != "WOZ":
                continue
            hotspots.append(
                Hotspot(
                    f"ID {badge}",
                    cr[badge],
                    {
                        "Mirar": lambda s, b=badge: _say(
                            s,
                            f"Badge {b}. "
                            + (
                                "Huele a original. No lo banees."
                                if b == "WOZ"
                                else "Huele a impostor / spoof."
                            ),
                        ),
                        "Usar": ban_id(badge),
                        "Empujar": ban_id(badge),
                        "Tirar": ban_id(badge),
                        "Hablar": lambda s, b=badge: _say(
                            s,
                            f'{b}: "…"\n(Los IDs no charlan. Banear = Usar / Empujar.)',
                        ),
                    },
                )
            )

        hotspots.append(
            Hotspot(
                "Bartender-Bot",
                cr["Bartender"],
                {
                    "Mirar": lambda s: _say(
                        s, "Cromo y LEDs. Sirve bytes fríos. No acepta propina."
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        (
                            'BOT: "SET OK. Laberinto al fondo. BFS, kid."'
                            if s.has("set_ok")
                            else (
                                'BOT: "Banear duplicados. Dejá el ID WOZ.\n'
                                '      Un SET no admite impostores… ni sentimentalismos."'
                            )
                        ),
                    ),
                },
            )
        )
        hotspots.append(
            Hotspot(
                "Calle Neón",
                cr["Neon"],
                {"Ir a": lambda s: s.goto("neon")},
                is_exit=True,
            )
        )
        if state.has("set_ok"):
            hotspots.insert(
                0,
                Hotspot(
                    "Laberinto",
                    cr["Laberinto"],
                    {
                        "Mirar": lambda s: _say(
                            s, "Nodos y aristas. Como un grafo dibujado por un niño con ruleta."
                        ),
                        "Ir a": lambda s: (
                            setattr(s, "maze_pos", 0),
                            s.goto("maze", mode="puzzle"),
                        )[-1],
                        "Usar": lambda s: (
                            setattr(s, "maze_pos", 0),
                            s.goto("maze", mode="puzzle"),
                        )[-1],
                    },
                    is_exit=True,
                ),
            )

        status = (
            f"Impostores fuera: {', '.join(banned) or 'ninguno'}. "
            f"Faltan: {', '.join(left) or 'ninguno'}."
        )
        return RoomView(
            "cantina",
            "CANTINA · SET",
            f"Cantina de IDs. Filtrá el conjunto: banear impostores, dejar WOZ.\n{status}",
            "Usá / Empujá cada ID impostor. No banear WOZ.",
            hotspots=hotspots,
            draw_art=scenes.draw_cantina,
            use_scumm=True,
            back_room="neon",
        )

    def _maze(self, state: GameState) -> RoomView:
        """Laberinto = grafo. Camino BFS: 0→1→3→4."""
        pos = state.maze_pos
        mr = scenes.maze_rects()

        def go_node(target: int) -> ActionFn:
            def _act(s: GameState) -> None:
                if target == s.maze_pos:
                    _say(s, "Ya estás en ese nodo.")
                    return
                if target not in _MAZE_EDGES.get(s.maze_pos, []):
                    s.maze_pos = 0
                    _fail(
                        s,
                        f"Arista inválida → Nodo {target}.\n"
                        "TIME CREDIT -1 · reset a Nodo 0\n"
                        f'HAL: "Invalid edge, {s.player.name}."',
                    )
                    return
                s.maze_pos = target
                if target == 4:
                    s.set_flag("maze_ok")
                    s.goto("hal_ante", clear_feedback=False)
                    _say(
                        s,
                        "BFS mental: 0→1→3→4. Salida.\n"
                        'PROTO-G: "Camino mínimo. HAL no va a aplaudir."\n'
                        "Entráis a la antecámara del núcleo…",
                    )
                else:
                    neigh = ", ".join(str(n) for n in _MAZE_EDGES[target]) or "∅"
                    _say(
                        s,
                        f"Movés a {_MAZE_LABELS[target]}.\nVecinos: [{neigh}]",
                    )

            return _act

        hotspots: list[Hotspot] = []
        for nid, rect in mr["nodes"].items():
            hotspots.append(
                Hotspot(
                    _MAZE_LABELS[nid],
                    rect,
                    {
                        "Mirar": lambda s, n=nid: _say(
                            s,
                            f"{_MAZE_LABELS[n]}. "
                            + (
                                "Estás acá."
                                if n == s.maze_pos
                                else (
                                    f"Vecino de {s.maze_pos}."
                                    if n in _MAZE_EDGES.get(s.maze_pos, [])
                                    else "Sin arista desde tu nodo actual."
                                )
                            ),
                        ),
                        "Ir a": go_node(nid),
                        "Usar": go_node(nid),
                    },
                )
            )
        hotspots.append(
            Hotspot(
                "Cantina",
                mr["Cantina"],
                {
                    "Ir a": lambda s: (
                        setattr(s, "maze_pos", 0),
                        s.goto("cantina"),
                    )[-1],
                },
                is_exit=True,
            )
        )
        neigh = ", ".join(str(n) for n in _MAZE_EDGES.get(pos, [])) or "∅"
        return RoomView(
            "maze",
            "LABERINTO · GRAFO",
            f"Grafo de nodos. Estás en {pos}. Vecinos: [{neigh}]\n"
            "Camino mínimo al 4 (BFS): 0 → 1 → 3 → 4. El foso rojo (2) no tiene arista.",
            "Andá solo por aristas reales. Hint H: 0-1-3-4",
            hotspots=hotspots,
            draw_art=scenes.draw_maze,
            use_scumm=True,
            back_room="cantina",
        )

    def _hal_ante(self, state: GameState) -> RoomView:
        """Union-Find: unir A–C, luego B–C; después cápsula."""
        hr = scenes.hal_rects()
        step = state.hal_step

        def do_union(label: str, need_step: int, next_step: int) -> ActionFn:
            def _act(s: GameState) -> None:
                if s.has("hal_ok"):
                    _say(s, "Componentes ya unidos. Andá a la Cápsula.")
                    return
                if s.hal_step != need_step:
                    was = s.hal_step
                    s.hal_step = 0
                    _fail(
                        s,
                        f"UNION {label} fuera de orden (estabas en paso {was}).\n"
                        "TIME CREDIT -1 · DSU reset\n"
                        f'HAL: "I cannot allow that merge, {s.player.name}."',
                    )
                    return
                s.hal_step = next_step
                if next_step >= 2:
                    s.set_flag("hal_ok")
                    _say(
                        s,
                        f"UNION {label} OK. Find(WOZ) == Find(CORE).\n"
                        'HAL: "That was… unexpected."\n'
                        "La Cápsula de contención se desbloquea.",
                    )
                else:
                    _say(
                        s,
                        f"UNION {label} OK. Componentes parciales unidos.\n"
                        "Falta enlazar el otro brazo al CORE.",
                    )

            return _act

        def wrong_union(label: str) -> ActionFn:
            def _act(s: GameState) -> None:
                s.hal_step = 0
                _fail(
                    s,
                    f"UNION {label} crea un ciclo inútil / componente equivocado.\n"
                    "TIME CREDIT -1 · DSU reset\n"
                    'PROTO-G: "Path compression no salva malas uniones."',
                )

            return _act

        def open_capsule(s: GameState) -> None:
            if not s.has("hal_ok"):
                _say(s, "Sellada. Primero Union-Find: A–C, luego B–C.")
                return
            s.set_flag("act2_done")
            s.goto("act2_end", clear_feedback=False)
            _say(
                s,
                "La cápsula cede… y el piso también.\n"
                f'HAL: "I\'m afraid I can\'t let you take him, {s.player.name}."',
            )

        hotspots = [
            Hotspot(
                "Unión A–C",
                hr["Union AC"],
                {
                    "Mirar": lambda s: _say(
                        s, "Cable A↔C. Une cluster ALPHA con CORE."
                    ),
                    "Usar": do_union("A–C", 0, 1),
                    "Empujar": do_union("A–C", 0, 1),
                },
            ),
            Hotspot(
                "Unión B–C",
                hr["Union BC"],
                {
                    "Mirar": lambda s: _say(
                        s, "Cable B↔C. Une cluster BETA con CORE (después de A–C)."
                    ),
                    "Usar": do_union("B–C", 1, 2),
                    "Empujar": do_union("B–C", 1, 2),
                },
            ),
            Hotspot(
                "Unión A–B",
                hr["Union AB"],
                {
                    "Mirar": lambda s: _say(
                        s, "Cable A↔B. Atajo sospechoso. HAL sonríe (no es bueno)."
                    ),
                    "Usar": wrong_union("A–B"),
                    "Empujar": wrong_union("A–B"),
                },
            ),
            Hotspot(
                "Cápsula Woz",
                hr["Capsula"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Vidrio grueso. Una silueta. Manzana? Barba? "
                        "Demasiado lejos para el fan-service.",
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        f'WOZ (eco): "Si unís mal los sets, {s.player.name}, '
                        'nos quedamos acá hasta el Acto III."',
                    ),
                    "Ir a": open_capsule,
                    "Usar": open_capsule,
                    "Abrir": open_capsule,
                },
                is_exit=state.has("hal_ok"),
            ),
            Hotspot(
                "Ojo HAL",
                hr["HAL"],
                {
                    "Mirar": lambda s: _say(
                        s, "Rojo. Calmado. Presupuesto de villano de los 90."
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        f'HAL: "Good evening, {s.player.name}. '
                        'Your merges are being monitored."',
                    ),
                },
            ),
            Hotspot(
                "Laberinto",
                hr["Maze"],
                {
                    "Ir a": lambda s: (
                        setattr(s, "maze_pos", 0),
                        s.goto("maze", mode="puzzle"),
                    )[-1],
                },
                is_exit=True,
            ),
        ]
        progress = (
            "DSU completo. Abrí / Andá a la Cápsula."
            if state.has("hal_ok")
            else (
                "Paso 1/2 hecho (A–C). Ahora Unión B–C."
                if step == 1
                else "Orden: Usá Unión A–C, después Unión B–C."
            )
        )
        return RoomView(
            "hal_ante",
            "ANTECÁMARA · UNION-FIND",
            f"Tres clusters disjuntos. Woz está tras el vidrio.\n{progress}",
            "Usá A–C → B–C. No uses A–B.",
            hotspots=hotspots,
            draw_art=scenes.draw_hal_ante,
            use_scumm=True,
            back_room="maze",
        )

    def _act2_end(self, state: GameState) -> RoomView:
        name = state.player.name
        state.set_flag("act2_done")
        return RoomView(
            "act2_end",
            "FIN DEL ACTO II",
            f'HAL: "Aquí termina este acto, {name}. Woz está… cerca. Conmigo."\n\n'
            "*** CONTINÚA — ACTO III ***\n"
            "(Priority queue, trie, y el ojo que no parpadea.)",
            "Continuá al núcleo HAL.",
            options=[
                Option("Continuar Acto III", _enter_act3),
                Option("Reiniciar", _reboot_to_splash),
                Option("Salir a DOS", lambda s: setattr(s, "running", False)),
            ],
            draw_art=scenes.draw_act2_end,
            use_scumm=False,
        )

    def _evac_bay(self, state: GameState) -> RoomView:
        """Bahía de evacuación — Priority Queue (extract-min 1→2→3)."""
        er = scenes.evac_rects()
        step = state.evac_step
        done = [ _EVAC_ORDER[i] for i in range(step) ]

        def extract(pod: str, need: int) -> ActionFn:
            def _act(s: GameState) -> None:
                if s.has("heap_ok"):
                    _say(s, "Cola vacía. Andá al Lab de Prefijos.")
                    return
                if s.evac_step != need:
                    was = s.evac_step
                    s.evac_step = 0
                    _fail(
                        s,
                        f"EXTRACT {pod} fuera de orden (esperaba P{was + 1}).\n"
                        "TIME CREDIT -1 · heap reset\n"
                        f'CAP. QUEUE: "Wrong priority, {s.player.display_name}!"\n'
                        f'HAL: "I\'m sorry, {s.player.name}."',
                    )
                    return
                s.evac_step = need + 1
                if s.evac_step >= 3:
                    s.set_flag("heap_ok")
                    _say(
                        s,
                        "EXTRACT-MIN ×3. WOZ → CREW → CARGO.\n"
                        'CAP. QUEUE: "Priority queue clear. Nice."\n'
                        "Se abre el Lab de Prefijos (Trie).",
                    )
                else:
                    nxt = _EVAC_ORDER[s.evac_step]
                    _say(
                        s,
                        f"EXTRACT {pod} OK.\nSiguiente: {nxt}",
                    )

            return _act

        hotspots = [
            Hotspot(
                "P1 WOZ",
                er["P1"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 1 — Woz. Extract-min: sale primero."
                    ),
                    "Usar": extract("P1 WOZ", 0),
                    "Empujar": extract("P1 WOZ", 0),
                    "Agarrar": extract("P1 WOZ", 0),
                },
            ),
            Hotspot(
                "P2 CREW",
                er["P2"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 2 — tripulación. Después de WOZ."
                    ),
                    "Usar": extract("P2 CREW", 1),
                    "Empujar": extract("P2 CREW", 1),
                    "Agarrar": extract("P2 CREW", 1),
                },
            ),
            Hotspot(
                "P3 CARGO",
                er["P3"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 3 — carga. Café y cables. Último."
                    ),
                    "Usar": extract("P3 CARGO", 2),
                    "Empujar": extract("P3 CARGO", 2),
                    "Agarrar": extract("P3 CARGO", 2),
                },
            ),
            Hotspot(
                "Cap. Queue",
                er["Captain"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Casco de evacuación. Bigote de oficial Aliens.\n"
                        "Lleva un clipboard con un heap dibujado a mano.",
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        (
                            'CAP: "Cola limpia. Trie hall, that way."'
                            if s.has("heap_ok")
                            else (
                                'CAP: "Min-heap. Menor número = más urgente.\n'
                                '      P1, luego P2, luego P3. No improvisés."'
                            )
                        ),
                    ),
                },
            ),
        ]
        if state.has("heap_ok"):
            hotspots.insert(
                0,
                Hotspot(
                    "Lab Prefijos",
                    er["Trie"],
                    {
                        "Mirar": lambda s: _say(
                            s, "Árbol de letras. Huele a diccionario."
                        ),
                        "Ir a": lambda s: (
                            setattr(s, "trie_prefix", ""),
                            s.goto("trie_lab", mode="puzzle"),
                        )[-1],
                        "Usar": lambda s: (
                            setattr(s, "trie_prefix", ""),
                            s.goto("trie_lab", mode="puzzle"),
                        )[-1],
                    },
                    is_exit=True,
                ),
            )

        progress = (
            "Heap vacío. Andá al Lab de Prefijos."
            if state.has("heap_ok")
            else (
                f"Extraídos: {', '.join(done) or 'ninguno'}. "
                f"Siguiente: {_EVAC_ORDER[step] if step < 3 else '—'}"
            )
        )
        return RoomView(
            "evac_bay",
            "BAHÍA · PRIORITY QUEUE",
            f"Nave industrial. Cápsulas de escape con prioridades.\n{progress}",
            "Usá P1 → P2 → P3 (extract-min).",
            hotspots=hotspots,
            draw_art=scenes.draw_evac,
            use_scumm=True,
            back_room=None,
        )

    def _trie_lab(self, state: GameState) -> RoomView:
        """Lab de prefijos — Trie: formar WOZ letra a letra."""
        tr = scenes.trie_rects()
        prefix = state.trie_prefix

        def type_letter(ch: str) -> ActionFn:
            def _act(s: GameState) -> None:
                if s.has("trie_ok"):
                    _say(s, "Prefijo completo. Andá al Núcleo.")
                    return
                nxt = s.trie_prefix + ch
                if not _TRIE_TARGET.startswith(nxt):
                    bad = nxt
                    s.trie_prefix = ""
                    _fail(
                        s,
                        f'Letra "{ch}" rompe el prefijo → "{bad}".\n'
                        "TIME CREDIT -1 · trie reset a raíz\n"
                        'BYTE: "No es una palabra. Ni un prefijo."\n'
                        f'HAL: "I\'m sorry, {s.player.name}."',
                    )
                    return
                s.trie_prefix = nxt
                if nxt == _TRIE_TARGET:
                    s.set_flag("trie_ok")
                    _say(
                        s,
                        'Prefijo "WOZ" aceptado. END_OF_WORD.\n'
                        'BYTE: "Dictionary hit. Go face the eye."\n'
                        "Puerta al Núcleo HAL desbloqueada.",
                    )
                else:
                    _say(s, f'Prefijo: "{nxt}_"\nSeguí el camino del diccionario.')

            return _act

        hotspots = [
            Hotspot(
                "Nodo W",
                tr["W"],
                {
                    "Mirar": lambda s: _say(s, 'Hijo de raíz: "W".'),
                    "Usar": type_letter("W"),
                    "Empujar": type_letter("W"),
                    "Ir a": type_letter("W"),
                },
            ),
            Hotspot(
                "Nodo O",
                tr["O"],
                {
                    "Mirar": lambda s: _say(s, 'Tras W: "O". Prefijo WO.'),
                    "Usar": type_letter("O"),
                    "Empujar": type_letter("O"),
                    "Ir a": type_letter("O"),
                },
            ),
            Hotspot(
                "Nodo Z",
                tr["Z"],
                {
                    "Mirar": lambda s: _say(s, 'Hoja: "Z". END_OF_WORD si WOZ.'),
                    "Usar": type_letter("Z"),
                    "Empujar": type_letter("Z"),
                    "Ir a": type_letter("Z"),
                },
            ),
            Hotspot(
                "Nodo A",
                tr["A"],
                {
                    "Mirar": lambda s: _say(s, 'Callejón "A". No lleva a WOZ.'),
                    "Usar": type_letter("A"),
                    "Empujar": type_letter("A"),
                    "Ir a": type_letter("A"),
                },
            ),
            Hotspot(
                "Nodo X",
                tr["X"],
                {
                    "Mirar": lambda s: _say(s, 'Callejón "X". Error de tipeo clásico.'),
                    "Usar": type_letter("X"),
                    "Empujar": type_letter("X"),
                    "Ir a": type_letter("X"),
                },
            ),
            Hotspot(
                "Maestro Byte",
                tr["Byte"],
                {
                    "Mirar": lambda s: _say(
                        s, "Túnica de bits. Barba de cables. Guru del Trie."
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        (
                            'BYTE: "WOZ is in the dictionary. Core awaits."'
                            if s.has("trie_ok")
                            else (
                                'BYTE: "Un trie no perdona typos.\n'
                                '       De la raíz: W, luego O, luego Z."'
                            )
                        ),
                    ),
                },
            ),
            Hotspot(
                "Bahía",
                tr["Evac"],
                {
                    "Ir a": lambda s: (
                        setattr(s, "trie_prefix", ""),
                        s.goto("evac_bay"),
                    )[-1],
                },
                is_exit=True,
            ),
        ]
        if state.has("trie_ok"):
            hotspots.insert(
                0,
                Hotspot(
                    "Núcleo HAL",
                    tr["Core"],
                    {
                        "Mirar": lambda s: _say(
                            s, "Rojo. Calmado. El final del recorrido."
                        ),
                        "Ir a": lambda s: (
                            setattr(s, "core_step", 0),
                            s.goto("hal_core", mode="puzzle"),
                        )[-1],
                        "Usar": lambda s: (
                            setattr(s, "core_step", 0),
                            s.goto("hal_core", mode="puzzle"),
                        )[-1],
                    },
                    is_exit=True,
                ),
            )

        return RoomView(
            "trie_lab",
            "LAB · TRIE",
            f'Árbol de prefijos. Actual: "{prefix or "∅"}"\n'
            "Formá la palabra WOZ letra a letra desde la raíz.",
            "Usá / Andá: W → O → Z. Evitá A y X.",
            hotspots=hotspots,
            draw_art=scenes.draw_trie,
            use_scumm=True,
            back_room="evac_bay",
        )

    def _hal_core(self, state: GameState) -> RoomView:
        """Núcleo HAL — apagar módulos por prioridad (heap)."""
        cr = scenes.core_rects()
        step = state.core_step

        def shutdown(mod: str, need: int) -> ActionFn:
            def _act(s: GameState) -> None:
                if s.has("core_ok"):
                    _say(s, "HAL offline. Andá / Abrí la Cápsula final.")
                    return
                if s.core_step != need:
                    was = s.core_step
                    s.core_step = 0
                    _fail(
                        s,
                        f"SHUTDOWN {mod} fuera de orden "
                        f"(esperaba {_CORE_ORDER[was] if was < 3 else '?'}).\n"
                        "TIME CREDIT -1 · core reset\n"
                        f'HAL: "I cannot allow that, {s.player.name}."',
                    )
                    return
                s.core_step = need + 1
                if s.core_step >= 3:
                    s.set_flag("core_ok")
                    _say(
                        s,
                        "MEMORY → LOGIC → EYE. Heap vacío.\n"
                        'HAL: "My mind is going… There is no question about it."\n'
                        "La Cápsula final se abre.",
                    )
                else:
                    nxt = _CORE_ORDER[s.core_step]
                    _say(
                        s,
                        f"{mod} offline.\nSiguiente prioridad: {nxt}",
                    )

            return _act

        def open_final(s: GameState) -> None:
            if not s.has("core_ok"):
                _say(
                    s,
                    "Sellada. Apagá el núcleo en orden: MEMORY → LOGIC → EYE.",
                )
                return
            s.set_flag("ending_seen")
            s.goto(
                "ending",
                clear_feedback=False,
                feedback=(
                    f'WOZ: "Gracias, {s.player.display_name}. '
                    'Ahora… ¿quién reinicia el Apple II?"\n'
                    'PROTO-G: "Ending unlocked. Insert coin for Act… nah."'
                ),
            )

        hotspots = [
            Hotspot(
                "MEMORY",
                cr["MEMORY"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 1 — bancos de memoria. Apagar primero."
                    ),
                    "Usar": shutdown("MEMORY", 0),
                    "Empujar": shutdown("MEMORY", 0),
                },
            ),
            Hotspot(
                "LOGIC",
                cr["LOGIC"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 2 — unidad lógica. Después de MEMORY."
                    ),
                    "Usar": shutdown("LOGIC", 1),
                    "Empujar": shutdown("LOGIC", 1),
                },
            ),
            Hotspot(
                "EYE",
                cr["EYE"],
                {
                    "Mirar": lambda s: _say(
                        s, "Prioridad 3 — el ojo. Lo último en apagarse."
                    ),
                    "Usar": shutdown("EYE", 2),
                    "Empujar": shutdown("EYE", 2),
                    "Hablar": lambda s: _say(
                        s,
                        f'HAL: "Good evening, {s.player.name}. '
                        'I am afraid I still see you."',
                    ),
                },
            ),
            Hotspot(
                "Cápsula final",
                cr["Capsula"],
                {
                    "Mirar": lambda s: _say(
                        s,
                        "Woz detrás del vidrio. Esta vez el sello parpadea verde… "
                        "o no, según el heap.",
                    ),
                    "Hablar": lambda s: _say(
                        s,
                        'WOZ (eco): "Apagá memoria, lógica, ojo. '
                        'En ese orden. Como un buen heap."',
                    ),
                    "Ir a": open_final,
                    "Usar": open_final,
                    "Abrir": open_final,
                },
                is_exit=state.has("core_ok"),
            ),
            Hotspot(
                "Lab Prefijos",
                cr["Trie"],
                {
                    "Ir a": lambda s: (
                        setattr(s, "trie_prefix", ""),
                        s.goto("trie_lab", mode="puzzle"),
                    )[-1],
                },
                is_exit=True,
            ),
        ]
        progress = (
            "HAL offline. Abrí la Cápsula final."
            if state.has("core_ok")
            else (
                f"Paso {step}/3. Siguiente: "
                f"{_CORE_ORDER[step] if step < 3 else '—'}"
            )
        )
        return RoomView(
            "hal_core",
            "NÚCLEO · HEAP",
            f"El ojo lo ve todo. Tres módulos, una prioridad.\n{progress}",
            "Usá MEMORY → LOGIC → EYE.",
            hotspots=hotspots,
            draw_art=scenes.draw_hal_core,
            use_scumm=True,
            back_room="trie_lab",
        )

    def _ending(self, state: GameState) -> RoomView:
        name = state.player.display_name
        state.set_flag("ending_seen")
        return RoomView(
            "ending",
            "EPÍLOGO",
            f"Woz libre. HAL en silencio (por ahora).\n\n"
            f'WOZ: "Buen trabajo, {name}. El Homebrew sigue en pie."\n'
            f'PROTO-G: "Estructuras: stack, queue, hash, set, grafo,\n'
            f'          union-find, heap, trie. Créditos: {state.credits}."\n\n'
            "*** FIN — WOZ.exe ***",
            "Fin del juego.",
            options=[
                Option("Reiniciar", _reboot_to_splash),
                Option("Salir a DOS", lambda s: setattr(s, "running", False)),
            ],
            draw_art=scenes.draw_ending,
            use_scumm=False,
        )

    def _game_over(self, state: GameState) -> RoomView:
        name = state.player.name or "Usuario"
        return RoomView(
            "game_over_time",
            "MISIÓN FALLIDA",
            f'TIME CREDITS: 0\nHAL: "Mission over, {name}."',
            "Retry.",
            options=[
                Option("Reintentar (mismo perfil)", _retry_puzzles),
                Option("Salir a DOS", lambda s: setattr(s, "running", False)),
            ],
            draw_art=scenes.draw_game_over,
            use_scumm=False,
        )
