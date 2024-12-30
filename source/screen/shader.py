import pygame
from pygame import Surface

from source.utils.constants import *


class Shader:
    def __init__(self) -> None:
        self.filter = pygame.Surface(SCREEN_SIZE_T, pygame.SRCALPHA)
        self.filter.fill((16, 16, 16, 255))

        # Add horizontal scanlines
        #for y in range(0, SCREEN_SIZE_T[1], 2):
        #    pygame.draw.line(self.filter, (16, 16, 16, 32), (0, y), (SCREEN_SIZE_T[0], y), 1)

        # Add vertical scanlines
        for x in range(0, SCREEN_SIZE_T[0], 2):
            pygame.draw.line(self.filter, (16, 16, 16, 32), (x, 0), (x, SCREEN_SIZE_T[1]), 1)

        # Add noise to the crt filter
        #for _ in range(1000):  # Noise points
        #    pygame.draw.circle(self.filter, (16, 16, 16, randint(50, 150)), (randint(0, SCREEN_SIZE_T[0]), randint(0, SCREEN_SIZE_T[1])), 1)

        self.filter.set_alpha(96, pygame.RLEACCEL)


    def render(self, screen: Surface) -> None:
        screen.blit(self.filter)
