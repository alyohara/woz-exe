"""Perfil del protagonista."""

from dataclasses import dataclass, field


VIBES = {
    "garage": {
        "label": "Chico del garage — curioso, soldador en la sangre",
        "short": "Chico del garage",
    },
    "operator": {
        "label": "Operador nocturno — café, dial-up y turnos raros",
        "short": "Operador nocturno",
    },
    "arcade": {
        "label": "Fantasma del arcade — fichas, high scores y neón",
        "short": "Fantasma del arcade",
    },
    "campus": {
        "label": "Cifrador del campus — apuntes y cripto amateur",
        "short": "Cifrador del campus",
    },
}


@dataclass
class Player:
    name: str = ""
    handle: str = ""
    vibe: str = ""
    inventory: list[str] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        if self.handle:
            return self.handle
        return self.name or "Usuario"

    @property
    def vibe_short(self) -> str:
        return VIBES.get(self.vibe, {}).get("short", "—")

    def profile_text(self) -> str:
        lines = [
            f"Nombre: {self.name or '???'}",
            f"Handle: {self.handle or '(ninguno)'}",
            f"Estilo: {self.vibe_short}",
            "",
            "Inventario:",
        ]
        if self.inventory:
            lines.extend(f"  - {item}" for item in self.inventory)
        else:
            lines.append("  (vacío)")
        return "\n".join(lines)

    def add_item(self, item: str) -> None:
        if item not in self.inventory:
            self.inventory.append(item)
