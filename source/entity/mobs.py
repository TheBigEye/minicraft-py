from source.entity.mob import Mob
from source.screen.sprites import Sprites


class Mobs:
    """ Mob manager """

    sheep = Mob(0, Sprites.SHEEP, 5, 0.028, False)
    pig = Mob(1, Sprites.PIG, 5, 0.030, False)
    vamp = Mob(2, Sprites.VAMP, 8, 0.035, True)

    @staticmethod
    def get(identifier: int) -> Mob:
        """ Get mob instance by ID """

        if isinstance(identifier, int):
            for mob in Mobs.__dict__.values():
                if isinstance(mob, Mob) and mob.id == identifier:
                    return mob
            raise ValueError(f"No mob found with ID: {identifier}")
        else:
            raise TypeError("Mob identifier must be an int (ID) or str (name)")
