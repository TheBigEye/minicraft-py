from __future__ import annotations

from typing import TYPE_CHECKING

from source.utils.constants import (
    CHUNK_SIZE, SCREEN_FULL_H, SCREEN_FULL_W,
    TILE_HALF_SIZE, TILE_MULT_SIZE, TILE_SIZE
)

if TYPE_CHECKING:
    from source.world.tile import Tile
    from source.world.world import World


class Chunk:
    """ Represents a chunk of tiles in the world """
    __slots__ = ('tiles', 'modified', 'x', 'y')

    # Screen boundaries for tiles culling
    RENDER_BOUNDS = (
        -TILE_MULT_SIZE, -TILE_MULT_SIZE,
        SCREEN_FULL_W + TILE_HALF_SIZE,
        SCREEN_FULL_H - TILE_HALF_SIZE
    )

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


    def copy(self) -> list[list[Tile]]:
        """ Create a copy of the chunk tiles """
        return [row[:] for row in self.tiles]


    def fill(self, tiles: list[list[Tile]]) -> None:
        """ Fill the chunk with new tiles """
        self.tiles = tiles
        self.modified = True


    def data(self) -> list[list[int]]:
        """ Get serializable tile data for saving """
        return [[tile.id for tile in row] for row in self.tiles]


    @staticmethod
    def empty() -> list[list[None]]:
        """ Create an empty chunk tile array """
        return [[None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]


    def render(self, world: World, camera_x: int, camera_y: int) -> None:
        """ Render this chunk's tiles """

        chunk_base_x = self.x * CHUNK_SIZE * TILE_SIZE + camera_x
        chunk_base_y = self.y * CHUNK_SIZE * TILE_SIZE + camera_y

        # Skip if chunk is completely outside screen bounds
        if (chunk_base_x > Chunk.RENDER_BOUNDS[2] or
            chunk_base_x + (CHUNK_SIZE * TILE_SIZE) < 0 or
            chunk_base_y > Chunk.RENDER_BOUNDS[3] or
            chunk_base_y + (CHUNK_SIZE * TILE_SIZE) < 0):
            return

        # Render chunk tiles
        for yt in range(CHUNK_SIZE):
            row = self.tiles[yt]
            wy = chunk_base_y + yt * TILE_SIZE
            if not Chunk.RENDER_BOUNDS[1] <= wy <= Chunk.RENDER_BOUNDS[3]:
                continue

            for xt in range(CHUNK_SIZE):
                tile = row[xt]
                wx = chunk_base_x + xt * TILE_SIZE
                if not Chunk.RENDER_BOUNDS[0] <= wx <= Chunk.RENDER_BOUNDS[2]:
                    continue

                # Update tile connectors if needed
                if not tile.solid or tile.id == world.tiles.stone.id:
                    world_x = self.x * CHUNK_SIZE + xt
                    world_y = self.y * CHUNK_SIZE + yt
                    tile.connectors = world.tilemap.connector(world, tile, world_x, world_y)

                tile.render(world, wx, wy)
