from source.level.tile import Tile
from source.screen.sprites import Sprites

class Tiles:
    """ Tile manager class handling tile resources """

    # Master tile list that maps index -> (name, tile instance)
    TILE_LIST = [
        ("empty",      Tile(0,  Sprites.NULL_TILE,    False, False, -1,  -1  )),
        ("ocean",      Tile(1,  Sprites.WATER,        False, True,  -1,  -1  )),
        ("water",      Tile(2,  Sprites.WATER,        False, True,  -1,  -1  )),
        ("river",      Tile(3,  Sprites.WATER,        False, True,  -1,  -1  )),
        ("sand",       Tile(4,  Sprites.SAND,         False, False,  5,   1  )),
        ("dirt",       Tile(5,  Sprites.DIRT,         False, False,  6,   1  )),
        ("hole",       Tile(6,  Sprites.HOLE,         False, False, -1,  -1  )),
        ("grass",      Tile(7,  Sprites.GRASS,        False, False,  5,   1  )),
        ("tallgrass",  Tile(8,  Sprites.NULL_TILE,    False, False,  7,   2  )),
        ("oak_tree",   Tile(9,  Sprites.OAK_TREE,     True,  False,  7,   16 )),
        ("birch_tree", Tile(10, Sprites.BIRCH_TREE,   True,  False,  7,   24 )),
        ("pine_tree",  Tile(11, Sprites.PINE_TREE,    True,  False,  15,  32 )),
        ("stone",      Tile(12, Sprites.NULL_TILE,    True,  False,  7,   32 )),
        ("gravel",     Tile(13, Sprites.NULL_TILE,    False, False,  5,   4  )),
        ("ice",        Tile(14, Sprites.ICE,          False, False,  2,   4  )),
        ("snow",       Tile(15, Sprites.SNOW,         False, False,  5,   1  )),
        ("frost",      Tile(16, Sprites.NULL_TILE,    False, False,  15,  2  )),
        ("iceberg",    Tile(17, Sprites.ICEBERG,      True,  False,  1,   8  )),
        ("cactus",     Tile(18, Sprites.CACTUS,       True,  False,  4,   8  ))
    ]

    # Create reverse lookup by name
    INDEX = {
        name: index for index, (name, _) in enumerate(TILE_LIST)
    }

    # Create tile instance attributes
    locals().update(
        {name: tile for name, tile in (item for item in TILE_LIST)}
    )

    @staticmethod
    def from_id(id: int) -> Tile:
        """Get tile instance by ID"""
        return Tiles.TILE_LIST[id][1]

    @staticmethod
    def from_name(name: str) -> Tile:
        """Get tile instance by name"""
        return Tiles.TILE_LIST[Tiles.INDEX[name]][1]
