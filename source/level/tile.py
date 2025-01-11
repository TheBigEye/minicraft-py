from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING

from pygame import Surface

from source.sound import Sound
from source.utils.constants import TILE_HALF_SIZE, TILE_SIZE

if TYPE_CHECKING:
    from source.level.world import World


class Tile:

    # Here we will have a lot of instances of this class, we can save a lot of memory by using __slots__
    __slots__ = ['id', 'sprite', 'solid', 'liquid', 'parent', 'health', 'sprites', 'connectors']

    def __init__(self, id: int, sprites: list[Surface], solid: bool, liquid: bool, parent: int, health: int) -> None:
        self.id = id
        self.solid = solid
        self.liquid = liquid
        self.parent = parent
        self.health = health

        self.sprites = sprites
        self.sprite = None

        if not self.sprite:
            # We check if are a Tree model
            if len(self.sprites) == 2:
                self.sprite = choice(self.sprites)

            # Or a normal tile model
            elif len(self.sprites) >= 9:
                # Get available base sprites (first one and any after index 8)
                base_sprites = [self.sprites[0]] + self.sprites[9:]
                # Randomly select one of the base variations
                self.sprite = choice(base_sprites)

            # else ...
            else:
                self.sprite = self.sprites[0]

        self.connectors = []


    def hurt(self, world: World, x: int, y: int, damage: int) -> None:
        if self.health > 0:
            self.health -= damage

            Sound.play("genericHurt")

            if (self.health <= 0) and (self.parent > 0):
                world.set_tile(x, y, self.parent)


    def render(self, world: World, x: int, y: int) -> None:

        # Normal tiles
        if self.id not in {9, 10, 11}:  # Tree IDs
            world.tile_buffer.append((self.sprite, (x, y)))
            # Add transitions to the appropriate buffer
            for sprite in self.connectors:
                world.tile_buffer.append((sprite, (x, y)))
        else:
            # Tree rendering
            world.depth_buffer.append((self.sprite, (((x - TILE_SIZE) + TILE_HALF_SIZE), y - 24)))


    def clone(self) -> Tile:
        """ Returns a copy of the tile instance """
        return self.__class__(self.id, self.sprites, self.solid, self.liquid, self.parent, self.health)
