from __future__ import annotations

import os
import pickle
import struct
import array

from typing import TYPE_CHECKING, BinaryIO

from pygame import Vector2

from source.entity.mobs import Mobs
from source.sound import Sound
from source.utils.region import Region

if TYPE_CHECKING:
    from source.core.player import Player
    from source.level.world import World
    from source.utils.updater import Updater


class TinyBinaryTag:
    """ (TBT) A tiny binary format for game save data serialization.

    This format provides a lightweight alternative to NBT, designed specifically
    for Minicraft Py save files. It supports basic data types and compounds.

    Supported types:
        - Strings (UTF-8 encoded)
        - Integers (8, 16, 32, 64 bit)
        - Floats (32, 64 bit)
        - Byte arrays
        - Integer arrays
        - Float arrays
        - Compounds (via pickle)

    Format specification:
        - Magic number: 'MCPY' (4 bytes)
        - Version: uint8 (1 byte)
        - Data sections: Multiple compound tags
    """

    @staticmethod
    def write_string(file, string): # type: (BinaryIO, str) -> None
        """ Write a UTF-8 encoded string with length prefix """
        encoded = string.encode('utf-8')
        file.write(struct.pack('!H', len(encoded)))
        file.write(encoded)

    @staticmethod
    def read_string(file): # type: (BinaryIO) -> str
        """ Read a UTF-8 encoded string with length prefix """
        length = struct.unpack('!H', file.read(2))[0]
        return file.read(length).decode('utf-8')

    @staticmethod
    def write_int(file: BinaryIO, value: int, bits: int = 32) -> None:
        """ Write an integer with specified bit width (8, 16, 32, or 64) """
        fmt = {8: 'b', 16: 'h', 32: 'i', 64: 'q'}[bits]
        file.write(struct.pack(f'!{fmt}', value))

    @staticmethod
    def read_int(file: BinaryIO, bits: int = 32) -> int:
        """Read an integer with specified bit width (8, 16, 32, or 64)."""
        fmt = {8: 'b', 16: 'h', 32: 'i', 64: 'q'}[bits]
        return struct.unpack(f'!{fmt}', file.read(bits // 8))[0]

    @staticmethod
    def write_float(file: BinaryIO, value: float, double: bool = False) -> None:
        """Write a float (32-bit) or double (64-bit) value."""
        fmt = 'd' if double else 'f'
        file.write(struct.pack(f'!{fmt}', value))

    @staticmethod
    def read_float(file: BinaryIO, double: bool = False) -> float:
        """Read a float (32-bit) or double (64-bit) value."""
        fmt = 'd' if double else 'f'
        size = 8 if double else 4
        return struct.unpack(f'!{fmt}', file.read(size))[0]

    @staticmethod
    def write_array(file, values, typecode): # type: (BinaryIO, list[int | float], str) -> None
        """Write an array of numbers (integers or floats).

        Args:
            file: Binary file object to write to
            values: List of numbers to write
            typecode: Array type code ('i' for int, 'f' for float, etc.)
        """
        arr = array.array(typecode, values)
        file.write(struct.pack('!I', len(arr)))
        arr.tofile(file)

    @staticmethod
    def read_array(file, typecode): # type: (BinaryIO, str) -> list[int | float]
        """Read an array of numbers (integers or floats).

        Args:
            file: Binary file object to read from
            typecode: Array type code ('i' for int, 'f' for float, etc.)
        """
        length = struct.unpack('!I', file.read(4))[0]
        arr = array.array(typecode)
        arr.fromfile(file, length)
        return arr.tolist()

    @staticmethod
    def write_compound(file, data): # type: (BinaryIO, dict) -> None
        """Write a compound (dictionary) using pickle protocol 4.

        This method is used for complex nested structures that don't need
        direct binary access.
        """
        pickle.dump(data, file, protocol=4)

    @staticmethod
    def read_compound(file): # type: (BinaryIO) -> dict
        """Read a compound (dictionary) using pickle."""
        return pickle.load(file)



class Saveload:
    @staticmethod
    def save(updater, world, player): # type: (Updater, World, Player) -> None
        """Save the game state including mobs."""
        os.makedirs('./saves', exist_ok=True)

        # Save world metadata and mobs
        with open('./saves/level.dat', 'wb') as level:
            # Write magic number and version
            level.write(b'MCPY')
            level.write(struct.pack('!B', 1))  # Version 1

            # Save header data
            header = {
                'seed': world.seed,
                'perm': world.perm,
                'spawn': (world.sx, world.sy),
                'ticks': updater.ticks
            }
            pickle.dump(header, level)

            # Save player data
            player_data = {
                'x': player.position.x,
                'y': player.position.y,
                'xo': player.offset.x,
                'yo': player.offset.y,
                'xd': player.xd,
                'yd': player.yd,
                'fx': player.facing.x,
                'fy': player.facing.y,
                'cx': player.cx,
                'cy': player.cy,
                'health': player.health,
                'energy': player.energy
            }
            pickle.dump(player_data, level)

            # Save mob data
            mob_data = []
            for mob in world.mobs:
                mob_data.append({
                    'id': mob.id,
                    'x': mob.position.x,
                    'y': mob.position.y,
                    'fx': mob.facing.x,
                    'fy': mob.facing.y,
                    'cx': mob.cx,
                    'cy': mob.cy,
                    'health': mob.health,
                    'hostile': mob.hostile,
                    'frame': mob.frame,
                    'timer': mob.timer
                })
            pickle.dump(mob_data, level)

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
        """Load the game state including mobs."""
        with open('./saves/level.dat', 'rb') as level:
            # Verify magic number and version
            if level.read(4) != b'MCPY':
                raise ValueError("Invalid save file format")

            if struct.unpack('!B', level.read(1))[0] != 1:
                raise ValueError("Unsupported save version")

            # Load header data
            header = pickle.load(level)
            world.seed = header['seed']
            world.perm = header['perm']
            world.sx, world.sy = header['spawn']
            updater.ticks = header['ticks']

            # Load player data
            player_data = pickle.load(level)
            player.position.x = float(player_data['x'])
            player.position.y = float(player_data['y'])

            player.offset.x = float(player_data['xo'])
            player.offset.y = float(player_data['yo'])

            player.xd = player_data['xd']
            player.yd = player_data['yd']

            player.facing.x = float(player_data['fx'])
            player.facing.y = float(player_data['fy'])

            player.cx = player_data['cx']
            player.cy = player_data['cy']
            player.health = player_data['health']
            player.energy = player_data['energy']

            # Load mob data
            try:
                mob_data = pickle.load(level)
                world.mobs.clear()  # Clear existing mobs before loading

                for mob_info in mob_data:
                    # Create new mob instance from saved ID
                    mob = Mobs.from_id(mob_info['id']).clone()

                    # Restore mob state
                    mob.position = Vector2(mob_info['x'], mob_info['y'])
                    mob.facing = Vector2(mob_info['fx'], mob_info['fy'])
                    mob.cx = mob_info['cx']
                    mob.cy = mob_info['cy']
                    mob.health = mob_info['health']
                    mob.hostile = mob_info['hostile']
                    mob.frame = mob_info['frame']
                    mob.timer = mob_info['timer']

                    world.mobs.append(mob)
            except EOFError:
                # Handle older save files that don't have mob data
                world.spawn_mobs()  # Regenerate mobs if none were saved

        Sound.play("eventSound")
        player.initialize(world, player.position.x, player.position.y)
        world.loaded = True
