from source.level.tile import Tile
from source.screen.sprites import Sprites

class Tiles:
    """ Tile manager class handling tile resources """

    # Define individual tiles as class attributes
    water =         Tile(0,  Sprites.WATER,      False, True,  -1, -1)
    sand =          Tile(1,  Sprites.SAND,       False, False,  2,  1)
    dirt =          Tile(2,  Sprites.DIRT,       False, False,  3,  1)
    hole =          Tile(3,  Sprites.HOLE,       False, False, -1, -1)
    grass =         Tile(4,  Sprites.GRASS,      False, False,  2,  1)
    flower =        Tile(5,  Sprites.NULL,       False, False,  4,  2)
    oak_tree =      Tile(6,  Sprites.OAK_TREE,   True,  False,  2, 16)
    birch_tree =    Tile(7,  Sprites.BIRCH_TREE, True,  False,  2, 24)
    pine_tree =     Tile(8,  Sprites.PINE_TREE,  True,  False,  2, 32)
    stone =         Tile(9,  Sprites.STONE,      True,  False,  2, 32)
    ice =           Tile(10, Sprites.ICE,        False, False,  0,  4)
    snow =          Tile(11, Sprites.SNOW,       False, False,  2,  1)
    iceberg =       Tile(12, Sprites.ICEBERG,    True,  False,  0,  8)
    cactus =        Tile(13, Sprites.CACTUS,     True,  False,  1,  8)

    @staticmethod
    def get(identifier: int) -> Tile:
        """ Get tile instance by ID """
        if isinstance(identifier, int):  # Search by ID
            for tile in Tiles.__dict__.values():
                if isinstance(tile, Tile) and tile.id == identifier:
                    return tile
            raise ValueError(f"No tile found with ID: {identifier}")
        else:
            raise TypeError("Tile identifier must be an int (ID)")
