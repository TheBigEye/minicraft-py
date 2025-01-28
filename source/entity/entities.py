from source.entity.entity import Entity

from source.entity.furniture.anvil import Anvil
from source.entity.furniture.chest import Chest
from source.entity.furniture.enchanter import Enchanter
from source.entity.furniture.furnace import Furnace
from source.entity.furniture.oven import Oven
from source.entity.furniture.workbench import Workbench

from source.entity.mob.pig import Pig
from source.entity.mob.sheep import Sheep
from source.entity.mob.vampire import Vampire
from source.entity.mob.zombie import Zombie


class Entities:
    """ Entity manager """

    pool: list[type[Entity]] = [
        Vampire, # EID 0
        Sheep,   # EID 1
        Pig,     # EID 2
        Zombie,  # EID 3

        # Reserved
        None,   # EID 4
        None,   # EID 5
        None,   # EID 6
        None,   # EID 7
        None,   # EID 8
        None,   # EID 9
        None,   # EID 10
        None,   # EID 11
        None,   # EID 12
        None,   # EID 13
        None,   # EID 14

        Workbench, # EID 15
        Anvil,     # EID 16
        Enchanter, # EID 17
        Oven,      # EID 18
        Furnace,   # EID 19
        Chest,     # EID 20
    ]

    @staticmethod
    def get(identifier: int) -> Entity:
        """ Get entity instance by ID """

        if isinstance(identifier, int):
            return Entities.pool[identifier]()
        else:
            raise TypeError("Entity identifier must be an int ID")
