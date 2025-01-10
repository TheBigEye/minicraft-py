from source.entity.mob import Mob
from source.screen.sprites import Sprites


class Mobs:
    """ Mob manager """

    MOBS_LIST = [
        # Mob Name   ID  Sprites List   Health Speed  Hostile?
        ("sheep", Mob(0, Sprites.SHEEP,  5,    0.028, False)),
        ("pig",   Mob(1, Sprites.PIG,    5,    0.030, False)),
        ("vamp",  Mob(2, Sprites.VAMP,   8,    0.035, True))
    ]

    # Create reverse lookup by name
    INDEX = {
        name: index for index, (name, _) in enumerate(MOBS_LIST)
    }

    # Create mob instance attributes
    locals().update(
        {name: mob for name, mob in (item for item in MOBS_LIST)}
    )

    @staticmethod
    def from_id(id: int) -> Mob:
        """ Get mob instance by ID """
        return Mobs.MOBS_LIST[id][1]

    @staticmethod
    def from_name(name: str) -> Mob:
        """ Get mob instance by name """
        return Mobs.MOBS_LIST[Mobs.INDEX[name]][1]
