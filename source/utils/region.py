from __future__ import annotations

import os
import pickletools

from pickle import dumps, loads
from typing import Dict, Tuple

# A humble attempt at chunk storage. It’s not Minecraft, but at least it fits in your pocket.
# If you were looking for performance or advanced features, you may want to try something else.
# But hey, it works... just don't tell anyone it’s a bit less impressive than the original.


class Region:
    """ Handles chunk storage in region files using a format similar to Minecraft's MCRegion """

    REGION_SIZE = 16  # 16x16 chunks per region, 8x8 tiles per chunk :)
    SECTOR_SIZE = 4096 # Disks quickly access 4096 byte sectors, so we can load things much faster
    HEADER_SIZE = (REGION_SIZE * REGION_SIZE) * 8  # 16x16 chunks * 8 bytes per entry

    __slots__ = ('chunks_dir', 'filename', 'positions')

    def __init__(self, world_dir, rx, ry): # type: (str, int, int) -> None
        """ Initialize a region file handler

        Args:
            world_dir: Path to world directory
            rx: Region X coordinate
            ry: Region Y coordinate
        """
        self.chunks_dir = os.path.join(world_dir, 'region')
        os.makedirs(self.chunks_dir, exist_ok=True)

        self.filename = os.path.join(self.chunks_dir, f'r.{rx}.{ry}.mcr')
        self.positions: Dict[Tuple[int, int], Tuple[int, int]] = {}  # (x, y) -> (offset, size)

        if os.path.exists(self.filename):
            self._load_header()
        else:
            self._create_new()


    def _create_new(self): # type: () -> None
        """ Create a new empty region file with a header """
        with open(self.filename, 'wb') as f:
            # Write empty header
            f.write(b'\x00' * Region.HEADER_SIZE)


    def _load_header(self) -> None:
        """ Load chunk positions from the region file header """
        with open(self.filename, 'rb') as f:
            header_data = f.read(Region.HEADER_SIZE)

            for index in range(Region.REGION_SIZE * Region.REGION_SIZE):
                offset = int.from_bytes(header_data[index * 8:index * 8 + 4], 'big')
                size = int.from_bytes(header_data[index * 8 + 4:index * 8 + 8], 'big')

                if offset > 0 and size > 0:
                    x = index % Region.REGION_SIZE
                    y = index // Region.REGION_SIZE
                    self.positions[(x, y)] = (offset, size)


    def _write_header(self) -> None:
        """ Update the region file header with current chunk positions """
        header_data = bytearray(Region.HEADER_SIZE)

        for (x, y), (offset, size) in self.positions.items():
            index = y * Region.REGION_SIZE + x
            header_data[index * 8:index * 8 + 4] = offset.to_bytes(4, 'big')
            header_data[index * 8 + 4:index * 8 + 8] = size.to_bytes(4, 'big')

        with open(self.filename, 'r+b') as f:
            f.write(header_data)


    def write_chunk(self, cx, cy, data): # type: (int, int, dict) -> None
        """ Write a chunk to the region file

        Args:
            cx: Local chunk X coordinate (0-15)
            cy: Local chunk Y coordinate (0-15)
            data: Chunk data to write
        """
        chunk_data = pickletools.optimize(dumps(data, protocol=5))
        chunk_size = len(chunk_data)

        with open(self.filename, 'r+b') as f:
            # Determine write position
            if (cx, cy) not in self.positions:
                f.seek(0, 2)  # Seek to end
                current_pos = max(f.tell(), Region.HEADER_SIZE)
            else:
                current_pos = self.positions[(cx, cy)][0]

            # Write chunk data
            f.seek(current_pos)
            f.write(chunk_data)

            # Update positions
            self.positions[(cx, cy)] = (current_pos, chunk_size)

            # Update header
            index = cy * Region.REGION_SIZE + cx
            f.seek(index * 8)
            f.write(current_pos.to_bytes(4, 'big') + chunk_size.to_bytes(4, 'big'))


    def read_chunk(self, cx, cy): # type: (int, int) -> dict | None
        """ Read a chunk from the region file

        Args:
            cx: Local chunk X coordinate (0-15)
            cy: Local chunk Y coordinate (0-15)

        Returns:
            Chunk data or None if chunk doesn't exist
        """

        if (cx, cy) not in self.positions:
            return None

        offset, size = self.positions[(cx, cy)]

        with open(self.filename, 'rb') as f:
            f.seek(offset)
            chunk_data = f.read(size)
            return loads(chunk_data)


    @staticmethod
    def get_region(chunk_x, chunk_y): # type: (int, int) -> tuple[int, int, int, int]
        """Convert chunk coordinates to region coordinates and local coordinates.

        Args:
            chunk_x: Global chunk X coordinate
            chunk_y: Global chunk Y coordinate

        Returns:
            Tuple of (region_x, region_y, local_chunk_x, local_chunk_y)
        """

        rx = chunk_x >> 4
        ry = chunk_y >> 4

        cx = chunk_x & 15
        cy = chunk_y & 15

        return rx, ry, cx, cy
