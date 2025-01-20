from __future__ import annotations

import os
import pickle
import pickletools
import struct

from typing import TYPE_CHECKING

from pygame import Vector2

from source.core.sound import Sound
from source.entity.entities import Entities
from source.utils.region import Region

if TYPE_CHECKING:
    from source.core.player import Player
    from source.core.updater import Updater
    from source.level.world import World


class Saveload:

    @staticmethod
    def save(updater: Updater, world: World, player: Player) -> None:
        """ Save the game state including mobs """
        os.makedirs('./saves', exist_ok=True)

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
            },

            'entities': [{
                'eid': entity.eid,
                'x': entity.position.x,
                'y': entity.position.y,
                'fx': entity.facing.x,
                'fy': entity.facing.y
            } for entity in world.entities]
        }

        # Save world metadata and mobs to a single pickle file
        with open('./saves/level.dat', 'wb') as level:
            # Write magic number and version
            level.write(b'MCPY')
            level.write(struct.pack('!B', 2))  # Version 2

            # Dump the entire save data into the file
            level.write(pickletools.optimize(pickle.dumps(data, protocol=5)))


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
    def load(updater, world, player): # type: (Updater, World, Player) -> None
        """ Load the game state """

        with open('./saves/level.dat', 'rb') as level:
            # Verify magic number and version
            if level.read(4) != b'MCPY':
                raise ValueError("Invalid save file format")

            if struct.unpack('!B', level.read(1))[0] != 2:
                raise ValueError("Unsupported save version")

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

            # Load mob data
            entities = data.get('entities', [])
            world.entities.clear()  # Clear existing mobs before loading

            for entity_data in entities:

                eid = entity_data['eid']

                # For avoid load particles
                if (eid < 0):
                    continue

                # Create new entity instance from saved EID
                entity = Entities.get(eid)

                # Restore mob state
                entity.position = Vector2(entity_data['x'], entity_data['y'])
                entity.facing = Vector2(entity_data['fx'], entity_data['fy'])

                world.add(entity)

            # Handle older save files if mob data is missing
            if not entities:
                world.populate()

        Sound.play("eventSound")
        player.initialize(world, player.position.x, player.position.y)
        world.loaded = True
