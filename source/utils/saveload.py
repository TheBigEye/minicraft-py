from __future__ import annotations
import pickle
import struct
import array
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union, BinaryIO

from source.core.mob import mobs
from source.core.tile import tiles
from source.game import Game
from source.sound import Sound

if TYPE_CHECKING:
    from source.core.player import Player
    from source.core.world import World
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
    def write_string(file: BinaryIO, string: str) -> None:
        """ Write a UTF-8 encoded string with length prefix """
        encoded = string.encode('utf-8')
        file.write(struct.pack('!H', len(encoded)))
        file.write(encoded)

    @staticmethod
    def read_string(file: BinaryIO) -> str:
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
    def write_array(file: BinaryIO, values: Union[List[int], List[float]], typecode: str) -> None:
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
    def read_array(file: BinaryIO, typecode: str) -> Union[List[int], List[float]]:
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
    def write_compound(file: BinaryIO, data: Dict) -> None:
        """Write a compound (dictionary) using pickle protocol 4.

        This method is used for complex nested structures that don't need
        direct binary access.
        """
        pickle.dump(data, file, protocol=4)

    @staticmethod
    def read_compound(file: BinaryIO) -> Dict:
        """Read a compound (dictionary) using pickle."""
        return pickle.load(file)



class Saveload:
    @staticmethod
    def save(updater: Updater, world: World, player: Player) -> None:
        # Convert chunks to ID-based format
        chunks = {
            chunk: [[tile.id for tile in row] for row in data]
            for chunk, data in world.chunks.items()
        }

        # Pack entities data
        entities = [
            {'id': mob.id, 'x': mob.x, 'y': mob.y}
            for mob in world.entities
        ]

        # Create data sections
        header = {
            'version': 1,
            'name': "A Nice World",
            'seed': world.seed,
            'perm': world.perm,
            'spawn': (world.sx, world.sy),
            'ticks': updater.ticks
        }

        player_data = {
            'x': player.position.x, 'y': player.position.y,
            'cx': player.cx, 'cy': player.cy,
            'xo': player.offset.x, 'yo': player.offset.y,
            'xd': player.xd, 'yd': player.yd,
            'fx': player.facing.x, 'fy': player.facing.y,
            'health': player.health, 'energy': player.energy
        }

        world_data = {
            'chunks': chunks,
            'entities': entities
        }

        # Write everything in binary format
        with open('./saves/world.dat', 'wb') as file:
            # Write magic number and version
            file.write(b'MCPY')
            file.write(struct.pack('!B', 1))  # Version 1

            # Write each section
            TinyBinaryTag.write_compound(file, header)
            TinyBinaryTag.write_compound(file, player_data)
            TinyBinaryTag.write_compound(file, world_data)

    @staticmethod
    def load(updater: Updater, world: World, player: Player) -> None:
        with open('./saves/world.dat', 'rb') as file:
            # Verify magic number and version
            magic = file.read(4)
            if magic != b'MCPY':
                raise ValueError("Invalid save file format")

            version = struct.unpack('!B', file.read(1))[0]
            if version != 1:
                raise ValueError(f"Unsupported save version: {version}")

            # Read sections
            header = TinyBinaryTag.read_compound(file)
            player_data = TinyBinaryTag.read_compound(file)
            world_data = TinyBinaryTag.read_compound(file)

        # Update player state
        player.position.x = float(player_data['x'])
        player.position.y = float(player_data['y'])
        player.cx = player_data['cx']
        player.cy = player_data['cy']
        player.offset.x = float(player_data['xo'])
        player.offset.y = float(player_data['yo'])
        player.xd = player_data['xd']
        player.yd = player_data['yd']
        player.facing.x = float(player_data['fx'])
        player.facing.y = float(player_data['fy'])
        player.health = player_data['health']
        player.energy = player_data['energy']

        # Update world state
        world.seed = header['seed']
        world.perm = header['perm']
        world.sx = float(header['spawn'][0])
        world.sy = float(header['spawn'][1])
        updater.ticks = header['ticks']

        # Rebuild chunks
        chunks = world_data['chunks']
        world.chunks = {
            chunk: [[tiles[Game.tile[id]].clone() for id in row] for row in data]
            for chunk, data in chunks.items()
        }

        # Rebuild entities
        entities = world_data['entities']
        world.entities = [mobs[Game.mobs[data['id']]].clone() for data in entities]
        for mob, data in zip(world.entities, entities):
            mob.x = data['x']
            mob.y = data['y']

        Sound.play("eventSound")
        player.initialize(world, player.position.x, player.position.y)
        world.loaded = True
