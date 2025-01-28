from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, Vector2

from source.utils.autoslots import auto_slots

if TYPE_CHECKING:
    from source.world.world import World
    from source.core.player import Player
    from source.screen.sprites import Sprites

@auto_slots
class Entity:

    def __init__(self):
        # Entity ID
        self.eid = -1

        self.world: World = None
        self.sprites: Sprites = None

        self.facing: Vector2 = Vector2(0, 1)
        self.position: Vector2 = Vector2(0, 0)


    def initialize(self, world: World):
        self.world = world
        self.sprites = world.sprites


    def update(self) -> None:
        pass


    def render(self, screen: Surface) -> None:
        pass


    def touched_by(self, player: Player) -> None:
        pass


    def remove(self) -> None:
        self.world.entities = [
            entity for entity in self.world.entities
            if entity.position != self.position
        ]


    def data(self) -> dict:
        """ Get serializable entity data for saving """
        return {
            'eid': self.eid,
            'x': self.position.x,
            'y': self.position.y,
            'fx': self.facing.x,
            'fy': self.facing.y
        }
