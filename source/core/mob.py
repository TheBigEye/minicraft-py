from __future__ import annotations

from random import choice, randint
from typing import TYPE_CHECKING

from source.core.tile import fluids
from source.game import Game
from source.sound import Sound
from source.utils.constants import *

if TYPE_CHECKING:
    from source.core.world import World


offsets = {
    'w': (0, -1),
    's': (0, 1),
    'a': (-1, 0),
    'd': (1, 0)
}

directions = [
    'w', 's', 'a', 'd'
]


class Mob:

    __slots__ = (
        'id',
        'char',
        'color',
        'health',
        'sprite',
        'facing',
        'x',
        'y'
    )

    def __init__(self, id: int, char: str, color: tuple, health: int) -> None:
        self.id = id
        self.char = char
        self.color = color
        self.health = health

        self.x = 0
        self.y = 0

        self.facing = choice(directions)

        self.sprite = Game.sprite(self.char, self.color, 0)


    def move(self, world: World) -> None:
        """ Move the mob in a random direction """
        if not self.can_move(world) or randint(0, 4) == 2:
            # Change direction if blocked
            self.facing = choice(directions)
        else:
            xo, yo = offsets[self.facing]
            self.x += xo
            self.y += yo


    def can_move(self, world: World) -> bool:
        """ Check if the mob can move in its current direction """
        xo, yo = offsets[self.facing]
        xd = self.x + xo
        yd = self.y + yo
        tile = world.get_tile(xd, yd)

        return tile.id not in fluids and not tile.solid


    def hurt(self, world: World, damage: int) -> None:
        """ Reduce the mob's health by a given amount """
        self.health -= damage

        Sound.play("genericHurt")

        if self.health <= 0:
            world.despawn_mob(self.x, self.y)


    def clone(self) -> Mob:
        return Mob(self.id, self.char, self.color, self.health)


mobs = {
    # NAME             ID,     CHAR,  COLOR,             HEALTH
    "pig":             Mob(0,  'P',   (253, 143, 160),   20),
    "sheep":           Mob(1,  'S',   (128, 128, 128),   20)
}
