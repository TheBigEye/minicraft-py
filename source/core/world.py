from __future__ import annotations

from random import randint, seed
from typing import TYPE_CHECKING

from pygame import Surface

from source.core.perlin import NOISE_SCALE, Perlin
from source.core.tiles import Tiles
from source.game import Game
from source.screen.debug import Debug
from source.utils.constants import *
from source.screen.tilemap import Tilemap
from source.utils.region import Region
from source.core.chunk import Chunk

if TYPE_CHECKING:
    from source.core.player import Player
    from source.core.tile import Tile

class World:
    def __init__(self, player: Player) -> None:
        self.seed = None  # Seed for terrain generation
        self.perm: list = []  # Permutation matrix for noise generation

        # Storage for terrain and chunks
        self.chunks: dict = {}
        self.ticks: int = 0

        # Spawn point
        self.sx: float = 0.0
        self.sy: float = 0.0

        self.player = player
        self.loaded = False

        self.tile_buffer = []
        self.depth_buffer = []


    def initialize(self, worldseed) -> None:
        self.seed = worldseed
        seed(self.seed)

        self.perm = Perlin.permutation()

        xp = int(self.player.position.x) // CHUNK_SIZE
        yp = int(self.player.position.y) // CHUNK_SIZE

        for cx in range((xp - 6), (xp + 6)):
            for cy in range((yp - 6), (yp + 6)):
                self.load_chunk(cx, cy)

        self.player.initialize(self, self.sx, self.sy)

        self.loaded = True


    def load_chunk(self, cx: int, cy: int) -> None:
        """Load or generate a chunk at the given coordinates."""
        if (cx, cy) in self.chunks:
            return

        # Try to load from region file first
        rx, ry, lcx, lcy = Region.get_region(cx, cy)
        region = Region('./saves', rx, ry)
        chunk_data = region.read_chunk(lcx, lcy)

        if chunk_data:
            # Reconstruct chunk from saved data
            chunk_tiles = [
                [Tiles.from_id(tile_id).clone() for tile_id in row]
                for row in chunk_data['tiles']
            ]
            chunk = Chunk(cx, cy, chunk_tiles)
            chunk.modified = False  # Loaded chunks start unmodified
        else:
            # Generate new chunk
            chunk_tiles = Chunk.empty()

            # Single pass: Generate terrain and trees
            for h in range(CHUNK_SIZE):
                wy = cy * CHUNK_SIZE + h
                ty = wy * NOISE_SCALE

                for w in range(CHUNK_SIZE):
                    wx = cx * CHUNK_SIZE + w
                    tx = wx * NOISE_SCALE

                    elevation = Perlin.heightmap(self.perm, tx, ty)
                    humidity = Perlin.humidity(self.perm, tx, ty)
                    temperature = Perlin.temperature(self.perm, tx, ty)

                    tile = Tiles.grass.clone()
                    can_place_tree = False
                    tree_type = None

                    # Generate base terrain
                    if elevation < 0.28:
                        tile = Tiles.ocean.clone()
                    elif (elevation > 0.28) and (elevation < 0.32):
                        tile = Tiles.iceberg.clone() if temperature < 0.25 else Tiles.ocean.clone()
                    elif (elevation > 0.32) and (elevation < 0.42):
                        tile = Tiles.ice.clone() if temperature < 0.25 else Tiles.water.clone()
                    elif (elevation > 0.42) and (elevation < 0.60):
                        tile = Tiles.snow.clone() if temperature < 0.25 else Tiles.sand.clone()
                    elif elevation < 1.75:
                        # Cold regions
                        if temperature < 0.25:
                            tile = Tiles.snow.clone()
                            if humidity > 0.4 and elevation > 0.75:
                                can_place_tree = randint(0, 8) == 4
                                tree_type = Tiles.pine_tree

                        # Cool/Temperate regions
                        elif temperature < 0.70:
                            tile = Tiles.grass.clone()
                            if humidity > 0.4 and elevation > 0.50:
                                can_place_tree = randint(0, 8) == 4
                                tree_type = Tiles.oak_tree

                        # Warm/Hot regions
                        else:
                            if humidity < 0.3:
                                tile = Tiles.sand.clone()
                            else:
                                tile = Tiles.grass.clone()
                                if humidity > 0.6 and elevation > 0.60:
                                    can_place_tree = randint(0, 8) == 4
                                    tree_type = Tiles.birch_tree if randint(0, 4) == 2 else Tiles.oak_tree

                    # Mountain biomes
                    elif elevation < 1.95:
                        tile = Tiles.stone.clone()
                    else:
                        tile = Tiles.gravel.clone()

                    # Add base terrain tile first
                    chunk_tiles[h][w] = tile

                    # Try placing a tree if conditions are met
                    if can_place_tree and tree_type and not tile.solid:
                        # Only try to place trees if we're not too close to chunk borders
                        if (w > 1 and w < CHUNK_SIZE - 2 and
                            h > 1 and h < CHUNK_SIZE - 2):

                            # Check 3x3 area for existing trees
                            can_place = True
                            for check_y in range(h - 1, h + 2):
                                for check_x in range(w - 1, w + 2):
                                    if chunk_tiles[check_y][check_x]:
                                        if chunk_tiles[check_y][check_x].id in {
                                            Tiles.oak_tree.id,
                                            Tiles.pine_tree.id,
                                            Tiles.birch_tree.id
                                        }:
                                            can_place = False
                                            break
                                if not can_place:
                                    break

                            if can_place:
                                chunk_tiles[h][w] = tree_type.clone()

                    # Check for spawnpoint
                    if self.sx == 0 and self.sy == 0:
                        if tile.id in {Tiles.grass.id, Tiles.sand.id, Tiles.snow.id}:
                            self.sx = wx
                            self.sy = wy

            chunk = Chunk(cx, cy, chunk_tiles)

        self.chunks[(cx, cy)] = chunk

    def unload_chunks(self, center_x: int, center_y: int) -> None:
        """ Unload chunks that are too far from the center coordinates """

        for (cx, cy) in list(self.chunks.keys()):
            if (abs(cx - center_x) > RENDER_RANGE_H + 2 or
                abs(cy - center_y) > RENDER_RANGE_V + 2):

                chunk = self.chunks[(cx, cy)]

                # Save modified chunks before unloading
                if chunk.modified:
                    rx, ry, lcx, lcy = Region.get_region(cx, cy)
                    region = Region('./saves', rx, ry)

                    chunk_data = {
                        'tiles': chunk.get_tiles()
                    }

                    region.write_chunk(lcx, lcy, chunk_data)

                del self.chunks[(cx, cy)]


    def get_tile(self, x: int, y: int) -> Tile:
        """ Get the character at coordinates in the world """

        chunk_coords = (x // CHUNK_SIZE, y // CHUNK_SIZE)
        if chunk := self.chunks.get(chunk_coords):
            return chunk.get_tile(x % CHUNK_SIZE, y % CHUNK_SIZE)

        self.load_chunk(*chunk_coords)
        return self.chunks[chunk_coords].get_tile(x % CHUNK_SIZE, y % CHUNK_SIZE)

    def set_tile(self, x: int, y: int, tile: int | Tile) -> None:
        """ Update the world map with the replacement tile """

        # Calculate the chunk coordinates
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE

        # Load the chunk at the calculated chunk coordinates
        self.load_chunk(cx, cy)

        # Determine the correct Tile object
        if isinstance(tile, int):
            tile = Tiles.from_id(tile).clone()
        else:
            tile = tile.clone()

        # Set the tile in the terrain
        self.chunks[(cx, cy)].set_tile(x % CHUNK_SIZE, y % CHUNK_SIZE, tile)

    # FIX FIX THIS SHIT: optimize this
    def daylight(self) -> int:
        if self.ticks < 3000:
            return 16 + (self.ticks * 239 // 3000)
        elif self.ticks < 16000:
            return 255
        elif self.ticks < 18000:
            return 255 - ((self.ticks - 16000) * 239 // 2000)
        else:
            return 16

    def render(self, screen: Surface) -> None:
        # Clear buffers at start
        self.tile_buffer.clear()
        self.depth_buffer.clear()

        # Pre-calculate camera position
        camera_x = int(SCREEN_HALF_W - (self.player.position.x * TILE_SIZE))
        camera_y = int(SCREEN_HALF_H - (self.player.position.y * TILE_SIZE))

        # Get player chunk position
        player_chunk_x = int(self.player.position.x) // CHUNK_SIZE
        player_chunk_y = int(self.player.position.y) // CHUNK_SIZE

        # Calculate visible chunk range
        chunk_range = (
            range(player_chunk_x - RENDER_RANGE_H - 1, player_chunk_x + RENDER_RANGE_H + 2),
            range(player_chunk_y - RENDER_RANGE_V - 1, player_chunk_y + RENDER_RANGE_V + 2)
        )

        # Screen boundaries for culling
        screen_bounds = (-TILE_MULT_SIZE, -TILE_MULT_SIZE, SCREEN_FULL_W + TILE_HALF_SIZE, SCREEN_FULL_H - TILE_HALF_SIZE)

        # Render visible chunks
        for chunk_x in chunk_range[0]:
            chunk_base_x = chunk_x * CHUNK_SIZE * TILE_SIZE + camera_x

            if chunk_base_x > SCREEN_FULL_W or chunk_base_x + (CHUNK_SIZE * TILE_SIZE) < 0:
                continue

            for chunk_y in chunk_range[1]:
                chunk_base_y = chunk_y * CHUNK_SIZE * TILE_SIZE + camera_y

                if chunk_base_y > SCREEN_FULL_H or chunk_base_y + (CHUNK_SIZE * TILE_SIZE) < 0:
                    continue

                chunk = self.chunks.get((chunk_x, chunk_y))
                if not chunk:
                    continue

                # Render chunk tiles
                for yt, row in enumerate(chunk.tiles):
                    wy = chunk_base_y + yt * TILE_SIZE
                    if not screen_bounds[1] <= wy <= screen_bounds[3]:
                        continue

                    for xt, tile in enumerate(row):
                        wx = chunk_base_x + xt * TILE_SIZE
                        if not screen_bounds[0] <= wx <= screen_bounds[2]:
                            continue

                        if not tile.solid:
                            world_x = chunk_x * CHUNK_SIZE + xt
                            world_y = chunk_y * CHUNK_SIZE + yt
                            tile.connectors = Tilemap.connector(self, tile, world_x, world_y)

                        tile.render(self, wx, wy)

        # Sort and render the buffers
        self.depth_buffer.extend(self.player.render(screen))

        for buffer in [self.tile_buffer, self.depth_buffer]:
            # Ordenamos usando la coordenada Y almacenada como tercer elemento de la tupla
            buffer.sort(key=lambda x: x[1][2] if len(x[1]) > 2 else x[1][1])
            # Al hacer el fblit, solo pasamos las coordenadas x, y (no la coordenada de sorting)
            screen.fblits([(sprite, (pos[0], pos[1])) for sprite, pos in buffer])

        screen.blit(Game.darkness)

        if Game.debug:
            Debug.render(
                screen,
                self.chunks,
                self.player.position.x, self.player.position.y,
                self.player.cx, self.player.cy
            )

    def update(self, ticks) -> None:
        """ Update chunks around the player's position """

        self.ticks = ticks % 24000

        rx = range(self.player.cx - 4, self.player.cx + 4)
        ry = range(self.player.cy - 3, self.player.cy + 3)

        # Iterate through the defined range of chunks
        for cx in rx:
            for cy in ry:
                self.load_chunk(cx, cy)

                # Update each chunk within the range
                if ticks % 32 == 0:
                    if randint(0, 8) == 4:
                        self.update_tiles(
                            (cx, cy),            # The chunk to update
                            Tiles.dirt,       # The tile to replace
                            Tiles.grass,      # The tile to replace with

                            # Tiles that can influence the replacement
                            [
                                Tiles.grass,
                                Tiles.tallgrass
                            ]
                        )

                # Check if it's time to spread water
                if ticks % 8 == 0:
                    self.update_tiles(
                        (cx, cy),            # The chunk to update
                        Tiles.hole,       # The tile to replace
                        Tiles.water,      # The tile to replace with

                        # Tiles that can influence the replacement
                        [
                            Tiles.ocean,
                            Tiles.water
                        ]
                    )

        if ticks % 512 == 0:
            """ Manage chunk loading/unloading around player """
            # Unload distant chunks
            self.unload_chunks(self.player.cx, self.player.cy)

    def update_tiles(self, chunk_coords: tuple, tile_target: Tile, parent: Tile, influences: list) -> None:
        chunk = self.chunks.get(chunk_coords)
        if not chunk:
            return

        target = tile_target.id
        replace = parent.clone()
        modified = False

        # Create a copy of the chunk tiles
        temp_chunk = [row[:] for row in chunk.tiles]

        # Iterate through each tile in the chunk
        for yt in range(CHUNK_SIZE):
            for xt in range(CHUNK_SIZE):

                # Check if the current tile matches the target tile
                if chunk.tiles[yt][xt].id == target:
                    # If influence_tiles is provided, check surrounding tiles
                    if self.tiles_around(chunk_coords, influences, xt, yt):
                        # Replace the target tile with the new tile
                        temp_chunk[yt][xt] = replace
                        modified = True
                        break

        # Update the terrain with the modified chunk if changes were made
        if modified:
            chunk.tiles = temp_chunk
            chunk.modified = True

    def tiles_around(self, chunk: tuple, tiles_around: list, x: int, y: int) -> bool:
        """ Check if any of the specified tiles are around the given coordinates """

        # Define the directions to check around the given coordinates
        directions = {
            (-1, 0), (1, 0), (0, -1), (0, 1)
        }

        # Check each direction for matching tiles
        for dy, dx in directions:
            new_chunk_x = chunk[0] + (x + dx) // CHUNK_SIZE
            new_chunk_y = chunk[1] + (y + dy) // CHUNK_SIZE

            # Retrieve the adjacent chunk from the terrain
            around_chunk = self.chunks.get((new_chunk_x, new_chunk_y))

            # Check if any adjacent tile matches the specified tile types
            if around_chunk:
                new_y = (y + dy) % CHUNK_SIZE
                new_x = (x + dx) % CHUNK_SIZE

                # Check if tile matches any target tile
                if around_chunk.tiles[new_y][new_x].id in [tile.id for tile in tiles_around]:
                    return True

        return False
