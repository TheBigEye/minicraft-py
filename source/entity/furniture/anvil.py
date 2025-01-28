from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface

from source.entity.furniture.furniture import Furniture
from source.utils.autoslots import auto_slots

if TYPE_CHECKING:
    from source.world.world import World

@auto_slots
class Anvil(Furniture):

    def __init__(self):
        super().__init__("Anvil")
        self.eid = 16

        self.speed = 0.050


    def initialize(self, world: World) -> None:
        super().initialize(world)

        self.sprite = self.sprites.ANVIL


    def render(self, screen: Surface):
        super().render(screen)
        self.world.surfaces.append(
            (self.sprite, (self.rx - 15, self.ry - 10, self.ry - 15))
        )
