from __future__ import annotations

from typing import TYPE_CHECKING

from source.utils.constants import (
    CHUNK_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH,
    TILE_HALF, TILE_MULT, TILE_SIZE
)

if TYPE_CHECKING:
    from source.world.tile import Tile
    from source.world.world import World


class Chunk:
    """ Represents a chunk of tiles in the world """
    __slots__ = ('tiles', 'modified', 'x', 'y')

    # Screen boundaries for regular tiles culling
    BOUNDS = (
        -TILE_MULT, -TILE_MULT,
        SCREEN_WIDTH + TILE_HALF,
        SCREEN_HEIGHT - TILE_HALF
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


    def _bounds(self, world: World, cx: int, cy: int) -> bool:
        """ Check if chunk is within extended render distance from player """

        # Only check extended bounds for custom worlds
        if not world.is_custom:
            return False

        pcx = int(world.player.position.x) // CHUNK_SIZE
        pcy = int(world.player.position.y) // CHUNK_SIZE

        dist_x = abs(self.x - pcx)
        dist_y = abs(self.y - pcy)

        return dist_x <= 3 and dist_y <= 3


    def render(self, world: World, camera_x: int, camera_y: int) -> None:
        """ Render this chunk's tiles """
        cx = self.x * CHUNK_SIZE * TILE_SIZE + camera_x  # Chunk base x
        cy = self.y * CHUNK_SIZE * TILE_SIZE + camera_y  # Chunk base y

        # Calculate if chunk is within extended bounds for large sprites in custom worlds
        far_render = self._bounds(world, cx, cy)

        # Only we culling the chunk if we are in a normal world
        if not world.is_custom:
            # Skip if chunk is completely outside bounds
            if (cx > Chunk.BOUNDS[2] or
                cx + (CHUNK_SIZE * TILE_SIZE) < 0 or
                cy > Chunk.BOUNDS[3] or
                cy + (CHUNK_SIZE * TILE_SIZE) < 0):
                return

        chunk_size = range(CHUNK_SIZE)

        # Render chunk tiles
        for yt in chunk_size:
            row = self.tiles[yt]
            wy = cy + yt * TILE_SIZE
            world_y = self.y * CHUNK_SIZE + yt

            for xt in chunk_size:
                tile = row[xt]
                wx = cx + xt * TILE_SIZE
                world_x = self.x * CHUNK_SIZE + xt

                # For custom worlds, use extended bounds for large sprites
                if tile.sprite.get_width() > TILE_SIZE and world.is_custom:
                    if not far_render:
                        continue

                # For normal worlds, use regular bounds for all sprites
                else:
                    if not (Chunk.BOUNDS[0] <= wx <= Chunk.BOUNDS[2] and
                           Chunk.BOUNDS[1] <= wy <= Chunk.BOUNDS[3]):
                        continue

                tile.connectors = world.tilemap.connector(world, tile, world_x, world_y)
                tile.render(world, wx, wy)
