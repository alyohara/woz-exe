"""Punto de entrada de WOZ.exe."""

import sys

import pygame

from aventura_woz import config
from aventura_woz.game import Game


def main() -> None:
    pygame.init()
    pygame.display.set_caption(
        "WOZ.exe — Leonardo Bianco · inspirado en Flavio Speche"
    )
    screen = pygame.display.set_mode(
        (config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.RESIZABLE
    )
    clock = pygame.time.Clock()
    game = Game()

    while game.state.running:
        dt = clock.tick(config.FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                w = max(event.w, 640)
                h = max(event.h, 400)
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
        game.handle_events(events)
        game.update(dt)
        w, h = screen.get_size()
        game.draw(screen, w, h)
        pygame.display.flip()

    game.music.stop()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
