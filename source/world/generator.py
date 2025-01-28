from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

from source.world.noise import Noise
from source.world.chunk import Chunk
from source.utils.constants import CHUNK_SIZE

if TYPE_CHECKING:
    from source.world.tiles import Tiles
    from source.world.tile import Tile

class Generator:

    def __init__(self, tiles: Tiles):
        self.tiles = tiles

        self.trees = {}


    def initialize(self) -> None:
        self.trees = {
            self.tiles.oak_tree.id,
            self.tiles.pine_tree.id,
            self.tiles.birch_tree.id
        }


    def make_chunk(self, cx: int, cy: int, perm: list) -> list[list[Tile]]:
        """
            Generate terrain for a single chunk.

            Arguments:
                cx (int): Chunk x-coordinate
                cy (int): Chunk y-coordinate
                perm (list): Permutation matrix for noise generation

            Returns:
                List[List]: 2D list of terrain tiles
        """

        chunk_tiles = Chunk.empty()

        for h in range(CHUNK_SIZE):
            wy = cy * CHUNK_SIZE + h
            ty = wy * Noise.NOISE_SCALE

            for w in range(CHUNK_SIZE):
                wx = cx * CHUNK_SIZE + w
                tx = wx * Noise.NOISE_SCALE

                # Get terrain parameters
                temp = Noise.temperature(perm, tx, ty)
                humidity = Noise.humidity(perm, tx, ty)
                elevation = Noise.heightmap(perm, tx, ty)

                # Terrain generation logic
                tile = self.get_tile(temp, humidity, elevation)

                # Add base terrain tile
                chunk_tiles[h][w] = tile

                # Try placing a tree
                if (not tile.solid and
                    1 < w < CHUNK_SIZE - 2 and
                    1 < h < CHUNK_SIZE - 2 and
                    random() < 0.125):

                    tree_type = self.get_tree(temp, humidity, elevation)

                    if tree_type:
                        # Check 3x3 area for existing trees
                        can_place = self.check_tree(chunk_tiles, h, w)

                        if can_place:
                            chunk_tiles[h][w] = tree_type.clone()

        return chunk_tiles


    def get_tile(self, temp: float, humidity: float, elevation: float) -> Tile:
        """ Determine tile type based on terrain parameters """

        # Water bodies
        if elevation < 0.32:
            if elevation < 0.28:
                return self.tiles.water.clone()

            if temp < 0.25:
                return self.tiles.iceberg.clone()
            return self.tiles.water.clone()

        # Shallow water
        elif elevation < 0.42:
            if temp < 0.25:
                return self.tiles.ice.clone()
            return self.tiles.water.clone()

        # Beach/Snow
        elif elevation < 0.60:
            if temp < 0.25:
                return self.tiles.snow.clone()

            if random() < 0.025:
                return self.tiles.cactus.clone()
            return self.tiles.sand.clone()

        # Main terrain
        elif elevation < 1.75:
            # Cold regions
            if temp < 0.25:
                return self.tiles.snow.clone()

            # Cool/Temperate regions
            if temp < 0.70:
                if random() < 0.090:
                    return self.tiles.flower.clone()
                return self.tiles.grass.clone()

            # Warm/Hot regions
            if humidity < 0.30:
                return self.tiles.sand.clone()
            return self.tiles.grass.clone()

        # Mountains
        else:
            if elevation < 1.95:
                return self.tiles.stone.clone()

            return self.tiles.dirt.clone()


    def get_tree(self, temp: float, humidity: float, elevation: float):
        """ Determine tree type based on terrain parameters """

        if elevation < 1.75:
            # Cold regions
            if temp < 0.25:
                if humidity > 0.40 and elevation > 0.75:
                    return self.tiles.pine_tree

            # Cool/Temperate regions
            elif temp < 0.70:
                if humidity > 0.40 and elevation > 0.50:
                    return self.tiles.oak_tree

            # Warm/Hot regions
            else:
                if humidity > 0.60 and elevation > 0.60:
                    if random() < 0.25:
                        return self.tiles.birch_tree
                    return self.tiles.oak_tree

        return None


    def check_tree(self, chunk_tiles: list[list[Tile]], h: int, w: int) -> bool:
        """ Check if a tree can be placed in a 3x3 area """

        if chunk_tiles[h][w].id == self.tiles.sand.id:
            return False

        for check_y in range(h - 1, h + 2):
            for check_x in range(w - 1, w + 2):
                if chunk_tiles[check_y][check_x] and chunk_tiles[check_y][check_x].id in self.trees:
                    return False
        return True
