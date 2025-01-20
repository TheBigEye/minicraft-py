from __future__ import annotations

from typing import TYPE_CHECKING

from source.utils.constants import CHUNK_SIZE

if TYPE_CHECKING:
    from source.level.tile import Tile


class Chunk:
    """ Represents a chunk of tiles in the world """
    __slots__ = ('tiles', 'modified', 'x', 'y')

    def __init__(self, x: int, y: int, tiles: list) -> None:
        self.x: int = x
        self.y: int = y
        self.tiles: list[list[Tile]] = tiles

        # New chunks are considered modified until saved
        self.modified: bool = True


    def get(self, x: int, y: int) -> Tile:
        """ Get a tile at local coordinates """
        return self.tiles[y][x]


    def set(self, x: int, y: int, tile: Tile) -> None:
        """ Set a tile at local coordinates """
        self.tiles[y][x] = tile
        self.modified = True


    def data(self) -> list[list[int]]:
        """ Get serializable tile data for saving """
        return [[tile.id for tile in row] for row in self.tiles]


    @staticmethod
    def empty() -> list[list[None]]:
        """ Create an empty chunk tile array """
        return [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
