from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface

from source.world.tile import Tile

if TYPE_CHECKING:
    from source.screen.sprites import Sprites


class Tiles:
    """ Tile manager class handling tile resources """

    def __init__(self, sprites: Sprites):
        self.sprites = sprites

    def initialize(self) -> None:
        # Define individual tiles as class attributes
        self.water =         Tile(0,  self.sprites.WATER,      False, True,  -1, -1)
        self.sand =          Tile(1,  self.sprites.SAND,       False, False,  2,  1)
        self.dirt =          Tile(2,  self.sprites.DIRT,       False, False,  3,  1)
        self.hole =          Tile(3,  self.sprites.HOLE,       False, False, -1, -1)
        self.grass =         Tile(4,  self.sprites.GRASS,      False, False,  2,  1)
        self.flower =        Tile(5,  self.sprites.FLOWERS,    False, False,  4,  1)
        self.oak_tree =      Tile(6,  self.sprites.OAK_TREE,   True,  False,  2, 16)
        self.birch_tree =    Tile(7,  self.sprites.BIRCH_TREE, True,  False,  2, 18)
        self.pine_tree =     Tile(8,  self.sprites.PINE_TREE,  True,  False,  2, 24)
        self.stone =         Tile(9,  self.sprites.STONE,      True,  False,  2, 24)
        self.ice =           Tile(10, self.sprites.ICE,        False, False,  0,  4)
        self.snow =          Tile(11, self.sprites.SNOW,       False, False,  2,  1)
        self.iceberg =       Tile(12, self.sprites.ICEBERG,    True,  False,  0,  8)
        self.cactus =        Tile(13, self.sprites.CACTUS,     True,  False,  1,  8)
        self.iron_ore =      Tile(14, self.sprites.IRON_ORE,   True,  False,  2, 26)

    def get(self, identifier: int) -> Tile:
        """ Get tile instance by ID """
        if isinstance(identifier, int):  # Search by ID
            for tile in self.__dict__.values():
                if isinstance(tile, Tile) and tile.id == identifier:
                    return tile
            raise ValueError(f"No tile found with ID: {identifier}")
        else:
            raise TypeError("Tile identifier must be an int (ID)")
