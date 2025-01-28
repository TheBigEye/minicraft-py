from __future__ import annotations

import os
import pickletools

from pickle import dumps, loads

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
        """
            Initialize a region file handler

            Arguments:
                world_dir: Path to world directory
                rx: Region X coordinate
                ry: Region Y coordinate
        """
        self.chunks_dir = os.path.join(world_dir, 'region')
        os.makedirs(self.chunks_dir, exist_ok = True)

        self.filename = os.path.join(self.chunks_dir, f'r.{rx}.{ry}.mcr')
        self.positions: dict[tuple[int, int], tuple[int, int]] = {}  # (x, y) -> (offset, size)

        if os.path.exists(self.filename):
            self._load_header()
        else:
            self._create_new()


    def _create_new(self): # type: () -> None
        """ Create a new empty region file with a header """
        with open(self.filename, 'wb') as file:
            # Write empty header
            file.write(b'\x00' * Region.HEADER_SIZE)


    def _load_header(self) -> None:
        """ Load chunk positions from the region file header """
        with open(self.filename, 'rb') as file:
            header_data = file.read(Region.HEADER_SIZE)

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

        with open(self.filename, 'r+b') as file:
            file.write(header_data)


    def write_chunk(self, cx, cy, data): # type: (int, int, dict) -> None
        """
            Write a chunk to the region file

            Arguments:
                cx: Local chunk X coordinate (0-15)
                cy: Local chunk Y coordinate (0-15)
                data: Chunk data to write
        """
        chunk_data = pickletools.optimize(dumps(data, protocol=5))
        chunk_size = len(chunk_data)

        with open(self.filename, 'r+b') as file:
            # Determine write position
            if (cx, cy) not in self.positions:
                file.seek(0, 2)  # Seek to end
                current_pos = max(file.tell(), Region.HEADER_SIZE)
            else:
                current_pos = self.positions[(cx, cy)][0]

            # Write chunk data
            file.seek(current_pos)
            file.write(chunk_data)

            # Update positions
            self.positions[(cx, cy)] = (current_pos, chunk_size)

            # Update header
            index = cy * Region.REGION_SIZE + cx
            file.seek(index * 8)
            file.write(current_pos.to_bytes(4, 'big') + chunk_size.to_bytes(4, 'big'))


    def read_chunk(self, cx, cy): # type: (int, int) -> dict | None
        """
            Read a chunk from the region file

            Arguments:
                cx: Local chunk X coordinate (0-15)
                cy: Local chunk Y coordinate (0-15)

            Returns:
                Chunk data or None if chunk doesn't exist
        """

        if (cx, cy) not in self.positions:
            return None

        offset, size = self.positions[(cx, cy)]

        with open(self.filename, 'rb') as file:
            file.seek(offset)
            chunk_data = file.read(size)
            return loads(chunk_data)


    def remove_chunk(self, cx, cy): # type: (int, int) -> bool
        """
            Remove a chunk from the region's header without deleting its data (faster)

            - Effectively makes the chunk inaccessible without permanent deletion

            Arguments:
                cx: Local chunk X coordinate (0-15)
                cy: Local chunk Y coordinate (0-15)

            Returns:
                Boolean indicating whether chunk was successfully unlinked
        """
        if (cx, cy) not in self.positions:
            return False

        # Remove chunk position from tracked positions
        del self.positions[(cx, cy)]

        # Rewrite the header to reflect chunk removal
        self._write_header()

        return True


    def delete_chunk(self, cx, cy): # type: (int, int) -> bool
        """
            Permanently delete a chunk from the region file (slow)

            - Completely eliminates the chunk's data and reference

            Arguments:
                cx: Local chunk X coordinate (0-15)
                cy: Local chunk Y coordinate (0-15)

            Returns:
                Boolean indicating whether chunk was successfully deleted and file compacted
        """
        if (cx, cy) not in self.positions:
            return False

        # Get current chunk's offset and size
        current_offset, current_size = self.positions[(cx, cy)]

        # Remove chunk position from tracked positions
        del self.positions[(cx, cy)]

        # Rewrite the header to reflect chunk removal
        self._write_header()

        # Compact file by shifting subsequent chunks
        with open(self.filename, 'r+b') as file:
            # Read all existing chunk data after the deleted chunk
            file.seek(0, 2)
            file_size = file.tell()

            chunks_to_move = {
                pos: offset for pos, (offset, _) in self.positions.items()
                if offset > current_offset
            }

            # Sort chunks by their current offset to process from bottom to top
            sorted_chunks = sorted(chunks_to_move.items(), key=lambda x: x[1])

            # Move each chunk
            for (move_cx, move_cy), move_offset in sorted_chunks:
                # Read chunk data
                file.seek(move_offset)
                chunk_data = file.read(self.positions[(move_cx, move_cy)][1])

                # Write chunk data to its new position
                new_offset = move_offset - current_size
                file.seek(new_offset)
                file.write(chunk_data)

                # Update positions
                self.positions[(move_cx, move_cy)] = (new_offset, len(chunk_data))

            # Truncate file to remove unused space
            file.truncate(file_size - current_size)

        # Update header with new positions
        self._write_header()

        return True


    def exists_chunk(self, cx, cy): # type: (int, int) -> bool
        """
            Check if a chunk is referenced in the region header

            Arguments:
                cx: Local chunk X coordinate (0-15)
                cy: Local chunk Y coordinate (0-15)

            Returns:
                Boolean indicating chunk presence
        """
        return (cx, cy) in self.positions


    def count_chunks(self) -> int:
        """ Count number of chunks in the region """
        return len(self.positions)


    @staticmethod
    def get_region(chunk_x, chunk_y): # type: (int, int) -> tuple[int, int, int, int]
        """
            Convert chunk coordinates to region coordinates and local coordinates

            Arguments:
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
