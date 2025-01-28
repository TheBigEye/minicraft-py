from __future__ import annotations

from typing import TYPE_CHECKING

from random import choice, randint

from pygame import Vector2

from source.entity.entities import Entities
from source.entity.particle.text import TextParticle

if TYPE_CHECKING:
    from source.core.player import Player
    from source.world.world import World
    from source.world.tile import Tile


class Tests:

    @staticmethod
    def spawn_mobs(world: World, player: Player) -> None:
        x = player.position.x + randint(-3, 3) + 1
        y = player.position.y + randint(-3, 3) + 1

        # Check if spawn location is valid (not on player and not in water/solid blocks)
        tile: Tile = world.get_tile(int(x), int(y))
        if not tile.solid and not tile.liquid and (int(x) != int(player.position.x) or int(y) != int(player.position.y)):
            mob = choice(Entities.pool[0:3])()
            mob.position = Vector2(x, y)
            world.add(mob)


    @staticmethod
    def clear_mobs(world: World, player: Player) -> None:
        world.entities.clear()
        world.add(TextParticle("LOL", player.position.x, player.position.y, (255, 0, 255)))


    @staticmethod
    def spawn_furniture(world: World, player: Player) -> None:
        x = player.position.x + randint(-3, 3) + 1
        y = player.position.y + randint(-3, 3) + 1

        # Check if spawn location is valid (not on player and not in water/solid blocks)
        tile: Tile = world.get_tile(int(x), int(y))
        if not tile.solid and not tile.liquid and (int(x) != int(player.position.x) or int(y) != int(player.position.y)):
            # Choice from entity pool, from index 15 to 20
            furniture = choice(Entities.pool[15:20])()
            furniture.position = Vector2(x, y)
            world.add(furniture)
