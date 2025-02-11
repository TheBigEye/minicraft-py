from pygame import Vector2

from source.entity.particle.particle import Particle
from source.screen.screen import Screen

class SmashParticle(Particle):

    def __init__(self, x: float, y: float) -> None:
        super().__init__()

        self.position = Vector2(x, y)


    def update(self) -> None:
        self.tick_time += 1

        if self.tick_time > 10:
            self.remove()

        super().update()


    def render(self, screen: Screen) -> None:
        self.world.surfaces.append((self.sprites.SMASH_PARTICLE, (self.rx, self.ry, self.ry + 24)))
