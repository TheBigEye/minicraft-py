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

    # Display setup
    screen: Surface = pygame.display.set_mode(SCREEN_SIZE_T, pygame.SRCALPHA, 32)
    buffer: Surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32).convert_alpha()

    # Window setup
    pygame.display.set_caption("Minicraft Potato Edition (VGA Mode 13h)")
    pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())

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
        [15, 7, 13,  5]
    ]

    # Pre-rendered surfaces
    overlay: Surface = None
    darkness: Surface = None


    @staticmethod
    def initialize() -> None:
        """ Initialize game resources and lists """
        Game._initialize_overlay()


    @staticmethod
    def quit() -> None:
        """ Quit the game """
        pygame.font.quit()
        pygame.quit()


    @staticmethod
    def _initialize_overlay() -> None:
        """ Initialize the overlay surface with dithering pattern """
        Game.overlay = pygame.Surface((200, 200), pygame.SRCALPHA, 32).convert_alpha()
        Game.overlay.fill((255, 255, 255, 0))

        for y in range(200):
            for x in range(200):
                distance = sqrt((x - 100) ** 2 + (y - 100) ** 2)
                if distance < 100:
                    dither_value = Game.dither[y % 4][x % 4]
                    alpha = max(0, 255 - (distance * 2.55) - (dither_value * 10))
                    Game.overlay.set_at((x, y), (0, 0, 0, alpha))

        """ Initialize the darkness surface """
        Game.darkness = pygame.Surface(Game.screen.get_size(), pygame.SRCALPHA, 32).convert_alpha()
        Game.darkness.fill((0, 0, 0, 255))
