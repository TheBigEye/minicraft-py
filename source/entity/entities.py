from source.entity.entity import Entity
from source.entity.pig import Pig
from source.entity.sheep import Sheep
from source.entity.vampire import Vampire
from source.entity.zombie import Zombie


class Entities:
    """ Entity manager """

    pool: list[type[Entity]] = [
        Vampire, # EID 0
        Sheep,   # EID 1
        Pig,     # EID 2
        Zombie   # Eid 3
    ]

    @staticmethod
    def get(identifier: int) -> Entity:
        """ Get mob instance by ID """

        if isinstance(identifier, int):
            return Entities.pool[identifier]()
        else:
            raise TypeError("Mob identifier must be an int ID")
