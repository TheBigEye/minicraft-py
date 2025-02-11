from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Font, Surface
import pygame

from source.screen.color import Color
from source.utils.constants import SCREEN_HALF, SCREEN_SIZE

if TYPE_CHECKING:
    from source.screen.sprites import Sprites


class Screen:

    def __init__(self):

        pygame.init()
        pygame.font.init()
        pygame.display.init()

        # Window setup
        pygame.display.set_mode(SCREEN_SIZE, pygame.SRCALPHA, 32).convert_alpha()
        pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())
        pygame.display.set_caption("Minicraft Potato Edition")

        self.buffer = pygame.display.get_surface() # get_surface is a pointer to the main window surface, is FASTER!
        self.overlay: Surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32).convert_alpha()
        self.darkness: Surface = pygame.Surface(self.buffer.get_size(), pygame.SRCALPHA, 32).convert_alpha()

        self.font: Font = pygame.font.Font("./assets/fonts/IBM_VGA.ttf", 16) # Used for game texts
        self.chars: Font = pygame.font.Font("./assets/fonts/IBM_BIOS.ttf", 8) # Used for game particles

        self.sprites: Sprites = None


    def initialize(self, sprites: Sprites) -> None:

        # We generate the dither for the lightning system
        self.overlay.fill((255, 255, 255, 0))
        self.darkness.fill((0, 0, 0, 255))

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
                    self.overlay.set_at((x, y), (0, 0, 0, int(alpha)))

        # Assing sprites reference
        self.sprites = sprites


    def update_light(self, daylight: int):
        self.darkness.set_alpha(255 - daylight)

        self.darkness.blit(
            self.overlay,
            ((SCREEN_HALF[0] - 96), (SCREEN_HALF[1] - 92) - 16),
            special_flags = pygame.BLEND_RGBA_SUB
        )

        self.buffer.blit(self.darkness)


    def draw_box(self, x: int, y: int, width: int, height: int) -> list:
        buffer = []

        for yy in range(y, y + height):
            for xx in range(x, x + width):

                if xx == x and yy == y:
                    buffer.append((self.sprites.GUI[5], (xx * 16, yy * 16))) # Top-left corner
                elif xx == (x + width - 1) and yy == y:
                    buffer.append((self.sprites.GUI[6], (xx * 16, yy * 16))) # Top-right corner
                elif xx == x and yy == (y + height - 1):
                    buffer.append((self.sprites.GUI[7], (xx * 16, yy * 16))) # Bottom-left corner
                elif xx == (x + width - 1) and yy == (y + height - 1):
                    buffer.append((self.sprites.GUI[8], (xx * 16, yy * 16))) # Bottom-right corner

                elif yy == y:
                    buffer.append((self.sprites.GUI[1], (xx * 16, yy * 16))) # Top border
                elif xx == x:
                    buffer.append((self.sprites.GUI[2], (xx * 16, yy * 16))) # Left border
                elif xx == x + width - 1:
                    buffer.append((self.sprites.GUI[3], (xx * 16, yy * 16))) # Right border
                elif yy == y + height - 1:
                    buffer.append((self.sprites.GUI[4], (xx * 16, yy * 16))) # Bottom border

                else:
                    # Background
                    buffer.append((self.sprites.GUI[0], (xx * 16, yy * 16)))

        return buffer


    def draw_text(self, text: str, x: int, y: int, fore: Color, back: Color, shadow: bool):
        buffer = []

        pass

    """
    @staticmethod
    def draw_frame(x, y, width, height, title):
        pass
    """
