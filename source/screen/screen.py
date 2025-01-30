from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Font, Surface
import pygame

from source.utils.constants import SCREEN_SIZE_T

if TYPE_CHECKING:
    from source.screen.sprites import Sprites


class Screen:

    def __init__(self):

        pygame.init()
        pygame.font.init()
        pygame.display.init()

        # Window setup
        pygame.display.set_mode(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
        pygame.display.set_icon(pygame.image.load('./assets/icon.png').convert_alpha())
        pygame.display.set_caption("Minicraft Potato Edition")

        self.buffer = pygame.display.get_surface() # get_surface is a pointer to the main window surface, is FASTER!
        self.overlay: Surface = pygame.Surface((200, 200), pygame.SRCALPHA, 32).convert_alpha()
        self.darkness: Surface = pygame.Surface(self.buffer.get_size(), pygame.SRCALPHA, 32).convert_alpha()

        self.font: Font = pygame.font.Font("./assets/fonts/IBM_VGA.ttf", 16) # Used for game texts
        self.chars: Font = pygame.font.Font("assets/fonts/IBM_BIOS.ttf", 8) # Used for game particles


    def initialize(self) -> None:
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


    def draw_box(self, sprites: Sprites, x: int, y: int, width: int, height: int) -> list:
        buffer = []

        for yy in range(y, y + height):
            for xx in range(x, x + width):

                if xx == x and yy == y:
                    buffer.append((sprites.GUI_TOP_LEFT_CORNER, (xx * 16, yy * 16)))
                elif xx == x + width - 1 and yy == y:
                    buffer.append((sprites.GUI_TOP_RIGHT_CORNER, (xx * 16, yy * 16)))
                elif xx == x and yy == y + height - 1:
                    buffer.append((sprites.GUI_BOTTOM_LEFT_CORNER, (xx * 16, yy * 16)))
                elif xx == x + width - 1 and yy == y + height - 1:
                    buffer.append((sprites.GUI_BOTTOM_RIGHT_CORNER, (xx * 16, yy * 16)))

                elif yy == y:
                    buffer.append((sprites.GUI_TOP_BORDER, (xx * 16, yy * 16)))
                elif yy == y + height - 1:
                    buffer.append((sprites.GUI_BOTTOM_BORDER, (xx * 16, yy * 16)))
                elif xx == x:
                    buffer.append((sprites.GUI_LEFT_BORDER, (xx * 16, yy * 16)))
                elif xx == x + width - 1:
                    buffer.append((sprites.GUI_RIGHT_BORDER, (xx * 16, yy * 16)))

                else:
                    buffer.append((sprites.GUI_BACKGROUND, (xx * 16, yy * 16)))

        return buffer

    """
    @staticmethod
    def draw_frame(x, y, width, height, title):
        pass


    @staticmethod
    def focus_nagger(self, updater: Updater, font: Font) -> list:

        # Calculate box position (convert pixels to tile units)
        x = (SCREEN_HALF_W // 16) - 6
        y = (SCREEN_HALF_H // 16) - 1

        # Create box and initialize sprites list
        sprites = Screen.draw_box(x, y, 12, 3)

        # Set color based on update count
        color = (128, 128, 128) if updater.count % 2 == 0 else (255, 255, 255)

        text = "Click to focus!"
        center_pos = (SCREEN_HALF_W, SCREEN_HALF_H - 7)

        # Create shadow text
        shadow = font.render(text, False, (0, 0, 0)).convert()
        shadow_rect = shadow.get_rect(center=(center_pos[0] + 1, center_pos[1] + 1))
        sprites.append((shadow, (shadow_rect.x, shadow_rect.y)))

        # Create main text
        message = font.render(text, False, color).convert()
        message_rect = message.get_rect(center=center_pos)
        sprites.append((message, (message_rect.x, message_rect.y)))

        return sprites
    """
