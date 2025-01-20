from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, Vector2

if TYPE_CHECKING:
    from source.level.world import World

class Entity:

    def __init__(self):
        # Entity ID
        self.eid = -1

        self.world: World = None

        self.facing: Vector2 = Vector2(0, 1)
        self.position: Vector2 = Vector2(0, 0)


    def initialize(self, world: World):
        self.world = world


    def update(self) -> None:
        pass


    def render(self, screen: Surface) -> None:
        pass


    def remove(self) -> None:
        self.world.entities = [
            entity for entity in self.world.entities
            if entity.position != self.position
        ]
