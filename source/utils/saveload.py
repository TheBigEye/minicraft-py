from __future__ import annotations

import os
import pickle
import pickletools

from typing import TYPE_CHECKING

from pygame import Vector2

from source.entity.entities import Entities
from source.utils.region import Region

if TYPE_CHECKING:
    from source.core.updater import Updater


class Saveload:

    @staticmethod
    def save(updater: Updater) -> None:
        """ Save the game state including mobs """
        os.makedirs('./saves', exist_ok=True)

        world = updater.world
        player = updater.player

        # Prepare data for saving
        data = {
            'header': {
                'seed': world.seed,
                'perm': world.perm,
                'spawn': (world.sx, world.sy),
                'ticks': updater.ticks
            },

            'player': {
                'x': player.position.x,
                'y': player.position.y,
                'xo': player.offset.x,
                'yo': player.offset.y,
                'fx': player.facing.x,
                'fy': player.facing.y,
                'xd': player.xd,
                'yd': player.yd,
                'cx': player.cx,
                'cy': player.cy,
                'health': player.health,
                'energy': player.energy
            }
        }

        # Save world metadata and player to level.dat
        with open('./saves/level.dat', 'wb') as level:
            level.write(b'MCPY')  # Magic number for security
            level.write(pickletools.optimize(pickle.dumps(data, protocol=5)))

        # Save entities to separate file
        entities_data = [entity.data() for entity in world.entities]

        with open('./saves/entities.dat', 'wb') as entities:
            entities.write(pickletools.optimize(pickle.dumps(entities_data, protocol=5)))

        # Save modified chunks to their region files
        for (cx, cy), chunk in world.chunks.items():
            if chunk.modified:
                rx, ry, lcx, lcy = Region.get_region(cx, cy)
                region = Region('./saves', rx, ry)

                data = {
                    'tiles': chunk.data()
                }

                region.write_chunk(lcx, lcy, data)
                chunk.modified = False


    @staticmethod
    def load(updater: Updater): # type: (Updater) -> None
        """ Load the game state """

        world = updater.world
        player = updater.player

        with open('./saves/level.dat', 'rb') as level:
            # Verify magic number
            if level.read(4) != b'MCPY':
                raise ValueError("Invalid save file format")

            # Load the entire saved data
            data = pickle.load(level)

            # Load header data
            header = data['header']
            world.seed = header['seed']
            world.perm = header['perm']
            world.sx, world.sy = header['spawn']
            updater.ticks = header['ticks']

            # Load player data
            player_data = data['player']
            player.position.x = float(player_data['x'])
            player.position.y = float(player_data['y'])
            player.offset.x = float(player_data['xo'])
            player.offset.y = float(player_data['yo'])
            player.facing.x = float(player_data['fx'])
            player.facing.y = float(player_data['fy'])

            player.xd = int(player_data['xd'])
            player.yd = int(player_data['yd'])
            player.cx = int(player_data['cx'])
            player.cy = int(player_data['cy'])

            player.health = player_data['health']
            player.energy = player_data['energy']

            world.initialize(world.seed, False)
            player.initialize(world, float(player_data['x']), float(player_data['y']))

        # Load entities
        try:
            with open('./saves/entities.dat', 'rb') as entities_file:
                entities = pickle.load(entities_file)
                world.entities.clear()

                for entity_data in entities:
                    eid = entity_data['eid']
                    # For avoid load particles and invalid entities
                    if (eid < 0):
                        continue

                    # Create new entity instance from saved EID
                    entity = Entities.get(eid)

                    # Restore mob state
                    entity.position = Vector2(entity_data['x'], entity_data['y'])
                    entity.facing = Vector2(entity_data['fx'], entity_data['fy'])

                    world.add(entity)

        except FileNotFoundError:
            # Handle case where entities file doesn't exist
            world.populate()

        world.loaded = True
