import pygame
from pygame import Surface

from source.utils.constants import SCREEN_SIZE_T

class Shader:
    def __init__(self) -> None:
        self.filter = pygame.Surface(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
        self.filter.fill((14, 14, 14, 255))

        # Add vertical scanlines
        for x in range(0, SCREEN_SIZE_T[0], 2):
            pygame.draw.line(self.filter, (14, 14, 14, 32), (x, 0), (x, SCREEN_SIZE_T[1]), 1)

        self.filter.set_alpha(96, pygame.RLEACCEL)


    def render(self, screen: Surface) -> None:
        screen.blit(self.filter)
