from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, Vector2

from source.entity.brain import PassiveBrain
from source.entity.mob.mob import Mob
from source.utils.autoslots import auto_slots


if TYPE_CHECKING:
    from source.entity.brain import Brain
    from source.world.world import World

@auto_slots
class Sheep(Mob):
    def __init__(self) -> None:
        super().__init__()

        # Entity ID
        self.eid = 1

        self.speed: float = 0.028
        self.brain: Brain = PassiveBrain(self)

        self.hostile: bool = False


    def initialize(self, world: World) -> None:
        super().initialize(world)

        self.sprites = self.sprites.SHEEP
        self.sprite = self.sprites[1][0]


    def update(self) -> None:
        super().update()

        # Update sprite
        movement = self.position - self.last_pos

        if movement.length() > 0:
            # Determine sprite direction based on movement
            if abs(movement.x) > abs(movement.y):
                sprite_row = 3 if movement.x > 0 else 2  # Right or Left
                self.facing = Vector2(1, 0) if movement.x > 0 else Vector2(-1, 0)
            else:
                sprite_row = 1 if movement.y > 0 else 0  # Down or Up
                self.facing = Vector2(0, 1) if movement.y > 0 else Vector2(0, -1)

            self.sprite = self.sprites[sprite_row][self.walk_dist % 2]
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


    def can_swim(self) -> bool:
        return False


    def render(self, screen: Surface):
        super().render(screen)
        self.world.surfaces.append(
            (self.sprite, (self.rx - 15, self.ry - 24, self.ry - 24))
        )
