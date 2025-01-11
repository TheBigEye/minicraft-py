from __future__ import annotations

from typing import TYPE_CHECKING

from random import choice, randint

from pygame import Vector2

from source.entity.mobs import Mobs

if TYPE_CHECKING:
    from source.core.player import Player
    from source.level.world import World
    from source.level.tile import Tile

class Tests:

    @staticmethod
    def spawn_mobs(world: World, player: Player) -> None:
        x = player.position.x + randint(-2, 2)
        y = player.position.y + randint(-2, 2)

        # Check if spawn location is valid (not in water/solid blocks)
        tile: Tile = world.get_tile(int(x), int(y))
        if not tile.solid and not tile.liquid:
        # Create random mob
            mob_type = choice([Mobs.sheep.id, Mobs.pig.id, Mobs.vamp.id])
            mob = Mobs.from_id(mob_type).clone()
            mob.position = Vector2(x, y)

            world.mobs.append(mob)
