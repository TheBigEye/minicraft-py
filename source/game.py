from __future__ import annotations

from math import sqrt

import pygame
from pygame import Surface
from pygame.font import Font

from source.utils.constants import SCREEN_SIZE_T


class Game:
    """Main game class handling core functionality and resources."""

    # Initialize Pygame modules
    pygame.init()
    pygame.font.init()
    pygame.display.init()

    # Window setup
    pygame.display.set_mode(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
    pygame.display.set_caption("Minicraft Potato Edition")
    pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())

    # Display setup
    buffer = pygame.display.get_surface()

    # Event filtering
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.TEXTINPUT])

    # Core game resources
    font: Font = pygame.font.Font("./assets/font.ttf", 16)
    debug: bool = False

    # Dithering pattern
    dither = [
        [0,  8,  2, 10],
        [12, 4, 14,  6],
        [3, 11,  1,  9],
        [15, 7, 13,  5],
    ]

    # Pre-rendered surfaces
    overlay: Surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32).convert_alpha()
    darkness: Surface = pygame.Surface(buffer.get_size(), pygame.SRCALPHA, 32).convert_alpha()

    @staticmethod
    def initialize() -> None:
        """ Initialize game resources """
        Game.overlay.fill((255, 255, 255, 0))

        for y in range(200):
            dy = y - 100
            yy = dy * dy  # (y - 100)^2

            for x in range(200):
                dx = x - 100
                xx = dx * dx  # (x - 100)^2

                distance = xx + yy
                if distance < 10000:  # 100^2
                    alpha = max(0, 255 - (distance * 0.0255) - (Game.dither[y % 4][x % 4] * 13))
                    Game.overlay.set_at((x, y), (0, 0, 0, int(alpha)))


        """ Initialize the darkness surface """
        Game.darkness.fill((0, 0, 0, 255))


    @staticmethod
    def quit() -> None:
        """ Quit the game """
        pygame.font.quit()
        pygame.quit()
