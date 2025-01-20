from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, Vector2

from source.entity.brain import NeutralBrain
from source.entity.mob import Mob
from source.screen.sprites import Sprites
from source.utils.slots import auto_slots

if TYPE_CHECKING:
    from source.entity.brain import Brain

@auto_slots
class Zombie(Mob):
    def __init__(self) -> None:
        super().__init__()

        # Entity ID
        self.eid = 3

        self.sprites = Sprites.ZOMBIE
        self.sprite = self.sprites[1][0]

        self.speed: float = 0.030
        self.timer: int = 0
        self.brain: Brain = NeutralBrain(self)


    def update(self) -> None:
        super().update()

        if (self.tick_time % 6 == 0) and (self.position != self.last_pos):
            self.timer = (self.timer + 1) % 2

        # Update sprite
        movement = self.position - self.last_pos

        if movement.length() > 0:
            # Determine sprite direction based on movement
            if abs(movement.x) > abs(movement.y):
                row = 3 if movement.x > 0 else 2  # Right or Left
                self.facing = Vector2(1, 0) if movement.x > 0 else Vector2(-1, 0)
            else:
                row = 1 if movement.y > 0 else 0  # Down or Up
                self.facing = Vector2(0, 1) if movement.y > 0 else Vector2(0, -1)

            self.sprite = self.sprites[row][self.timer]
        else:
            # Use standing sprite based on last facing direction
            if self.facing.y < 0:
                self.sprite = self.sprites[0][0]  # Up
            elif self.facing.y > 0:
                self.sprite = self.sprites[1][0]  # Down
            elif self.facing.x < 0:
                self.sprite = self.sprites[2][0]  # Left
            else:
                self.sprite = self.sprites[3][0]  # Right


    def render(self, screen: Surface):
        super().render(screen)

        self.world.surfaces.append((self.sprite, (self.rx - 15, self.ry - 24, self.ry - 24)))
