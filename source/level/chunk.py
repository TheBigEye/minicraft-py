from __future__ import annotations

from typing import TYPE_CHECKING

from source.utils.constants import CHUNK_SIZE

if TYPE_CHECKING:
    from source.level.tile.tile import Tile


class Chunk:
    """ Represents a chunk of tiles in the world """
    __slots__ = ('tiles', 'modified', 'x', 'y')

    def __init__(self, x: int, y: int, tiles) -> None: # type: (int, int, list[list[Tile]]) -> None
        self.x = x
        self.y = y
        self.tiles = tiles

        # New chunks are considered modified until saved
        self.modified = True


    def get(self, x: int, y: int): # type: (int, int) -> Tile
        """ Get a tile at local coordinates """
        return self.tiles[y][x]


    def set(self, x: int, y: int, tile): # type: (int, int, Tile) -> None
        """ Set a tile at local coordinates """
        self.tiles[y][x] = tile
        self.modified = True


    def data(self): # type: () -> list[list[int]]
        """ Get serializable tile data for saving """
        return [[tile.id for tile in row] for row in self.tiles]


    @staticmethod
    def empty(): # type: () -> list[list[None]]
        """ Create an empty chunk tile array """
        return [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
