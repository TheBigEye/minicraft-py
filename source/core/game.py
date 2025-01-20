from __future__ import annotations

import pygame
from pygame import Surface
from pygame.font import Font

from source.utils.constants import SCREEN_SIZE_T

class Game:
    """ Main game class """

    # Initialize Pygame modules
    pygame.init()
    pygame.font.init()
    pygame.display.init()

    # Window setup
    pygame.display.set_mode(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
    pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())
    pygame.display.set_caption("Minicraft Potato Edition")

    # Display setup
    buffer = pygame.display.get_surface() # get_surface is a pointer to the main window surface, is FASTER!
    overlay: Surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32).convert_alpha()
    darkness: Surface = pygame.Surface(buffer.get_size(), pygame.SRCALPHA, 32).convert_alpha()

    # Event filtering
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.TEXTINPUT])

    font: Font = pygame.font.Font("./assets/fonts/IBM_VGA.ttf", 16) # Used for game texts
    chars: Font = pygame.font.Font("./assets/fonts/IBM_BIOS.ttf", 8) # Used for game particles
    debug: bool = False

    # TODO: move initialize method to Screen class

    @staticmethod
    def initialize() -> None:
        """ Initialize game resources """

        ### lIGHT AND DARK OVERLAY ###
        Game.overlay.fill((255, 255, 255, 0))
        Game.darkness.fill((0, 0, 0, 255))

        # Dithering pattern
        dither = [
            [0,  8,  2, 10],
            [12, 4, 14,  6],
            [3, 11,  1,  9],
            [15, 7, 13,  5],
        ]

        for y in range(200):
            dy = y - 100
            yy = dy * dy  # (y - 100)^2

            for x in range(200):
                dx = x - 100
                xx = dx * dx  # (x - 100)^2

                distance = xx + yy
                if distance < 10000:  # 100^2
                    alpha = max(0, 255 - (distance * 0.0255) - (dither[y % 4][x % 4] * 13))
                    Game.overlay.set_at((x, y), (0, 0, 0, int(alpha)))


    @staticmethod
    def quit() -> None:
        """ Quit the game """
        pygame.display.quit()
        pygame.font.quit()
        pygame.quit()
