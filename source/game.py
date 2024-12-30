from __future__ import annotations

import pygame
from pygame import Surface
from pygame.font import Font
from typing import Dict, List, Tuple

from source.utils.constants import SCREEN_SIZE_T


class Game:
    """Main game class handling core functionality and resources."""

    # Initialize Pygame modules
    pygame.init()
    pygame.font.init()

    # Display setup
    screen: Surface = pygame.display.set_mode(SCREEN_SIZE_T, pygame.SRCALPHA, 32)
    buffer: Surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)

    # Window setup
    pygame.display.set_caption("Minicraft Potato Edition (VGA Mode 13h)")
    pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())

    # Event filtering
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.TEXTINPUT])

    # Core game resources
    font: Font = pygame.font.Font("./assets/terrain.ttf", 16)
    sprites: Dict[Tuple[str, Tuple, Tuple], Surface] = {}
    tile: List = []
    mobs: List = []
    debug: bool = False

    # Dithering pattern
    dither: List[List[int]] = [
        [0,  8,  2, 10],
        [12, 4, 14,  6],
        [3, 11,  1,  9],
        [15, 7, 13,  5]
    ]

    # Pre-rendered surfaces
    overlay: Surface = None
    darkness: Surface = None


    @staticmethod
    def initialize(tiles: dict, mobs: dict) -> None:
        """ Initialize game resources and lists """
        Game.tile = list(tiles)
        Game.mobs = list(mobs)
        Game._initialize_overlay()


    @staticmethod
    def _initialize_overlay() -> None:
        """ Initialize the overlay surface with dithering pattern """
        Game.overlay = pygame.Surface((200, 200), pygame.SRCALPHA, 32)
        Game.overlay.fill((255, 255, 255, 0))

        for y in range(200):
            for x in range(200):
                distance = ((x - 100) ** 2 + (y - 100) ** 2) ** 0.5
                if distance < 100:
                    dither_value = Game.dither[y % 4][x % 4]
                    alpha = max(0, 255 - (distance * 2.55) - (dither_value * 10))
                    Game.overlay.set_at((x, y), (0, 0, 0, alpha))

        """ Initialize the darkness surface """
        Game.darkness = pygame.Surface(Game.screen.get_size(), pygame.SRCALPHA, 32)
        Game.darkness.fill((0, 0, 0, 255))


    @staticmethod
    def sprite(char: str, foreground: tuple, background: tuple) -> Surface:
        """ Get or create a sprite with the given parameters

        Args:
            char: Character to render
            foreground: RGB color tuple for the character
            background: RGB color tuple for the background

        Returns:
            Surface: The requested sprite surface
        """
        key = (char, foreground, background)

        if key not in Game.sprites:
            Game.sprites[key] = Game.font.render(char, False, foreground, background).convert()

        return Game.sprites[key]
