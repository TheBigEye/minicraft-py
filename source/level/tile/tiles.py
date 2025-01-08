from source.level.tile.tile import Tile
from source.screen.sprites import Sprites

class Tiles:
    """ Tile manager class handling tile resources """

    # Master tile registry that maps ID -> (name, tile instance)
    REGISTRY = {
        0:  ("empty",      Tile(0,  Sprites.NULL_TILE,    False, False,   None,   None)),
        1:  ("ocean",      Tile(1,  Sprites.WATER,        False, True,    None,   None)),
        2:  ("water",      Tile(2,  Sprites.WATER,        False, True,    None,   None)),
        3:  ("river",      Tile(3,  Sprites.WATER,        False, True,    None,   None)),
        4:  ("sand",       Tile(4,  Sprites.SAND,         False, False,   5,      1   )),
        5:  ("dirt",       Tile(5,  Sprites.DIRT,         False, False,   6,      1   )),
        6:  ("hole",       Tile(6,  Sprites.HOLE,         False, False,   None,   None)),
        7:  ("grass",      Tile(7,  Sprites.GRASS,        False, False,   5,      1   )),
        8:  ("tallgrass",  Tile(8,  Sprites.NULL_TILE,    False, False,   7,      2   )),
        9:  ("oak_tree",   Tile(9,  Sprites.OAK_TREE,     True,  False,   7,      16  )),
        10: ("birch_tree", Tile(10, Sprites.BIRCH_TREE,   True,  False,   7,      24  )),
        11: ("pine_tree",  Tile(11, Sprites.PINE_TREE,    True,  False,   15,     32  )),
        12: ("stone",      Tile(12, Sprites.NULL_TILE,    True,  False,   7,      32  )),
        13: ("gravel",     Tile(13, Sprites.NULL_TILE,    False, False,   5,      4   )),
        14: ("ice",        Tile(14, Sprites.ICE,          False, False,   2,      4   )),
        15: ("snow",       Tile(15, Sprites.SNOW,         False, False,   5,      1   )),
        16: ("frost",      Tile(16, Sprites.NULL_TILE,    False, False,   15,     2   )),
        17: ("iceberg",    Tile(17, Sprites.ICEBERG,      True,  False,   1,      8   )),
        18: ("cactus",     Tile(18, Sprites.CACTUS,       True,  False,   4,      8   ))
    }

    # Create reverse lookup by name
    NAME_TO_ID = {
        name: id for id, (name, _) in REGISTRY.items()
    }

    # Create tile instance attributes
    locals().update(
        {
            name: tile for id, (name, tile) in REGISTRY.items()
        }
    )

    @classmethod
    def from_id(cls, id: int) -> Tile:
        """Get tile instance by ID"""
        return cls.REGISTRY[id][1]

    @classmethod
    def from_name(cls, name: str) -> Tile:
        """Get tile instance by name"""
        return cls.REGISTRY[cls.NAME_TO_ID[name]][1]