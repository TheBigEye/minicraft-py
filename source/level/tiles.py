from source.level.tile import Tile
from source.screen.sprites import Sprites

class Tiles:
    """ Tile manager class handling tile resources """

    # Define individual tiles as class attributes
    empty =         Tile(0, Sprites.NULL_TILE, False, False, -1, -1)
    ocean =         Tile(1, Sprites.WATER, False, True, -1, -1)
    water =         Tile(2, Sprites.WATER, False, True, -1, -1)
    river =         Tile(3, Sprites.WATER, False, True, -1, -1)
    sand =          Tile(4, Sprites.SAND, False, False, 5, 1)
    dirt =          Tile(5, Sprites.DIRT, False, False, 6, 1)
    hole =          Tile(6, Sprites.HOLE, False, False, -1, -1)
    grass =         Tile(7, Sprites.GRASS, False, False, 5, 1)
    tallgrass =     Tile(8, Sprites.NULL_TILE, False, False, 7, 2)
    oak_tree =      Tile(9, Sprites.OAK_TREE, True, False, 7, 16)
    birch_tree =    Tile(10, Sprites.BIRCH_TREE, True, False, 7, 24)
    pine_tree =     Tile(11, Sprites.PINE_TREE, True, False, 15, 32)
    stone =         Tile(12, Sprites.NULL_TILE, True, False, 7, 32)
    gravel =        Tile(13, Sprites.NULL_TILE, False, False, 5, 4)
    ice =           Tile(14, Sprites.ICE, False, False, 2, 4)
    snow =          Tile(15, Sprites.SNOW, False, False, 5, 1)
    frost =         Tile(16, Sprites.NULL_TILE, False, False, 15, 2)  # Unused
    iceberg =       Tile(17, Sprites.ICEBERG, True, False, 1, 8)
    cactus =        Tile(18, Sprites.CACTUS, True, False, 4, 8)

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
