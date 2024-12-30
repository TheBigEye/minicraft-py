from __future__ import annotations

### IMPORTANT
import pygame
from source.game import Game
###

from random import choice
from typing import TYPE_CHECKING

from pygame import Rect, Surface

from source.sound import Sound

from source.utils.constants import TILE_HALF_SIZE, TILE_SIZE
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.core.world import World


class Tile:

    __slots__ = (
        'id',
        'solid',
        'parent',
        'health',
        'sprites',
        'sprite',
        'connectors'
    )


    def __init__(self, id: int, sprites: list[Surface], solid: bool, parent: int | None, health: int | None) -> None:
        self.id = id
        self.solid = solid
        self.parent = parent
        self.health = health

        self.sprites = sprites
        self.sprite: Surface = None

        self.connectors = []


    def hurt(self, world: World, x: int, y: int, damage: int) -> None:
        if self.health is not None:
            self.health -= damage

            Sound.play("genericHurt")

            if (self.health <= 0) and (self.parent is not None):
                world.set_tile(x, y, self.parent)


    def render(self, world: World, x: int, y: int) -> None:

        if not self.sprite:
            self.sprite = choice(self.sprites)

        # Normal tiles
        if self.id not in {9, 10, 11}:
            world.tile_buffer.append((self.sprite, (x, y)))

            for con_type, sprite, offset in self.connectors:
                xo, yo = offset
                world.connectors[con_type].append((sprite, (x + xo, y + yo)))

        # Arboles
        else:
            world.depth_buffer.append((self.sprite, (((x - TILE_SIZE) + TILE_HALF_SIZE), y - 24)))


    def clone(self) -> Tile:
        """ Returns a copy of the tile instance """
        return self.__class__(self.id, self.sprites, self.solid, self.parent, self.health)


tiles = {
    # NAME               ID,   Sprites,                SOLID?,  PARENT, HEALTH
    "empty":         Tile(0,   Sprites.NULL_TILE,      False,   None,   None ),

    "ocean":         Tile(1,   Sprites.WATER,          False,   None,   None ),
    "water":         Tile(2,   Sprites.WATER,          False,   None,   None ),
    "river":         Tile(3,   Sprites.WATER,          False,   None,   None ),

    "sand":          Tile(4,   Sprites.SAND,           False,   5,      1    ),
    "dirt":          Tile(5,   Sprites.DIRT,           False,   6,      1    ),
    "hole":          Tile(6,   Sprites.NULL_TILE,      False,   None,   None ),
    "grass":         Tile(7,   Sprites.GRASS,          False,   5,      1    ),
    "tallgrass":     Tile(8,   Sprites.NULL_TILE,      False,   7,      2    ),

    "oak tree":      Tile(9,   Sprites.OAK_TREE,       True,    7,      16   ),
    "birch tree":    Tile(10,  Sprites.BIRCH_TREE,     True,    7,      24   ),
    "pine tree":     Tile(11,  Sprites.PINE_TREE,      True,    15,     32   ),

    "stone":         Tile(12,  Sprites.NULL_TILE,      True,    7,     32    ),
    "gravel":        Tile(13,  Sprites.NULL_TILE,      False,   5,      4    ),

    "ice":           Tile(14,  Sprites.ICE,            False,   2,      4    ),
    "snow":          Tile(15,  Sprites.SNOW,           False,   5,      1    ),
    "frost":         Tile(16,  Sprites.NULL_TILE,      False,   15,     2    ),
    "iceberg":       Tile(17,  Sprites.ICEBERG,        False,   1,      2    )
}


fluids = {
    tiles["ocean"].id,
    tiles["water"].id,
    tiles["river"].id
}
