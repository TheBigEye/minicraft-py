from source.entity.mob import Mob
from source.screen.sprites import Sprites


class Mobs:
    """ Mob manager """

    # Master mob registry
    REGISTRY = {
        1: ("sheep", Mob(1, Sprites.SHEEP, 5, 0.03, False)),
        2: ("pig", Mob(2, Sprites.PIG, 5, 0.03, False)),
        3: ("vamp", Mob(3, Sprites.VAMP, 8, 0.04, True))
    }

    # Create reverse lookup by name
    NAME_TO_ID = {
        name: id for id, (name, _) in REGISTRY.items()
    }

    # Create mob instance attributes
    locals().update(
        {
            name: mob for id, (name, mob) in REGISTRY.items()
        }
    )

    @classmethod
    def from_id(cls, id: int) -> Mob:
        """Get mob instance by ID"""
        return cls.REGISTRY[id][1]

    @classmethod
    def from_name(cls, name: str) -> Mob:
        """Get mob instance by name"""
        return cls.REGISTRY[cls.NAME_TO_ID[name]][1]
