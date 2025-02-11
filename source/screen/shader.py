from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from pygame import Surface
from pygame.draw import line

from source.utils.constants import SCREEN_SIZE

if TYPE_CHECKING:
    from source.screen.screen import Screen

# TODO: re-do this ... is slow due to alpha channel blending
# ... and also because we blit a big surface ._.

class Shader:
    def __init__(self) -> None:
        self.filter = Surface(SCREEN_SIZE, pygame.SRCALPHA, 32).convert_alpha()
        self.filter.fill((14, 14, 14, 255))

        # Add vertical scanlines
        for x in range(0, SCREEN_SIZE[0], 2):
            line(self.filter, (14, 14, 14, 32), (x, 0), (x, SCREEN_SIZE[1]), 1)

        #for y in range(0, SCREEN_SIZE[1], 2):
        #   line(self.filter, (14, 14, 14, 32), (0, y), (SCREEN_SIZE[0], y), 1)

        self.filter.set_alpha(96, pygame.RLEACCEL)


    def render(self, screen: Screen) -> None:
        screen.buffer.blit(self.filter)
