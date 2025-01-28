import random

import pygame
from pygame import Vector2

from source.entity.particle.particle import Particle
from source.screen.color import Color
from source.screen.screen import Screen
from source.screen.sprites import Sprites
from source.utils.autoslots import auto_slots


@auto_slots
class TextParticle(Particle):

    def __init__(self, message: str, x: float, y: float, color: tuple):
        super().__init__()
        self.message = message
        self.position = Vector2(x, y)
        self.color = color

        self.xx = float(x)
        self.yy = float(y)
        self.zz = 2.0

        self.xa: float = random.gauss() * 0.03
        self.ya: float = random.gauss() * 0.02
        self.za: float = random.uniform(0, 1) * 0.7 + 2

        self.text_width = len(self.message) * 16


    def update(self):
        self.tick_time += 1

        if (self.tick_time > 60):
            self.remove()

        # Python is a *bit* slower than java ...
        # so we need multiply these ...
        self.xx += self.xa * 1.1
        self.yy += self.ya * 1.1
        self.zz += self.za * 2

        if (self.zz < 0):
            self.zz = 0
            self.za *= -0.55
            self.xa *= 0.60
            self.ya *= 0.60

        self.za -= 0.16

        # Here we dont use int() since that the coords are float
        self.position.x = self.xx
        self.position.y = self.yy

        # For rendering position update
        super().update()

        # Adjust text position based on actual width
        self.rx -= self.text_width // 2
        self.ry -= int(self.zz)


    def render(self, screen: Screen) -> None:
        # Render text first
        self.text = screen.chars.render(self.message, False, self.color).convert()
        self.back = screen.chars.render(self.message, False, Color.BLACK).convert()

        # Scale maintaining aspect ratio for width, fixed height
        self.text = pygame.transform.scale(self.text, (self.text_width, 16))
        self.back = pygame.transform.scale(self.back, (self.text_width, 16))

        self.world.surfaces.extend([
            (self.back, (self.rx + 2, self.ry + 2, self.ry + 24)),
            (self.text, (self.rx, self.ry, self.ry + 24))
        ])
