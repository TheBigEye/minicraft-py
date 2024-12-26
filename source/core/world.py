from __future__ import annotations


from random import randint, seed
from typing import TYPE_CHECKING

from pygame import Surface

from source.core.mob import mobs
from source.core.perlin import NOISE_SCALE, Perlin
from source.core.tile import fluids, tiles
from source.game import Game
from source.screen.debug import Debug
from source.utils.constants import *
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.core.mob import Mob
    from source.core.player import Player
    from source.core.tile import Tile


class World:

    def __init__(self, player: Player) -> None:
        self.seed = None  # Seed for terrain generation
        self.perm: list = []  # Permutation matrix for noise generation

        # Storage for terrain and chunks
        self.chunks: dict = {}
        self.entities: list = []
        self.ticks: int = 0

        # Spawn point
        self.sx: float = 0.0
        self.sy: float = 0.0

        self.player = player
        self.loaded = False

        self.tile_buffer = []
        self.depth_buffer = []
        self.connectors = {
            'edge': [],
            'corner': [],
            'outer': []
        }


    def initialize(self, worldseed) -> None:
        self.seed = worldseed
        seed(self.seed)

        self.perm = Perlin.permutation()

        xp = int(self.player.position.x) // CHUNK_SIZE
        yp = int(self.player.position.y) // CHUNK_SIZE

        for cx in range((xp - 3), (xp + 3)):
            for cy in range((yp - 3), (yp + 3)):
                self.load_chunk(cx, cy)

        self.player.initialize(self, self.sx, self.sy)

        self.loaded = True


    def load_chunk(self, cx: int, cy: int) -> None:

        if (cx, cy) in self.chunks:
            return

        # We generaate a empty chunk first ...
        chunk = [
            [None for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)
        ]

        for h in range(CHUNK_SIZE):
            wy = cy * CHUNK_SIZE + h
            ty = wy * NOISE_SCALE

            for w in range(CHUNK_SIZE):
                wx = cx * CHUNK_SIZE + w
                tx = wx * NOISE_SCALE

                elevation = Perlin.heightmap(self.perm, tx, ty)
                humidity = Perlin.humidity(self.perm, tx, ty)
                temperature = Perlin.temperature(self.perm, tx, ty)

                tile = tiles["grass"].clone()

                # Generate the ocean
                if elevation < 0.28:
                    tile = tiles["ocean"].clone()

                elif (elevation > 0.28) and (elevation < 0.32):
                    if temperature < 0.25:
                        tile = tiles["iceberg"].clone()
                    else:
                        tile = tiles["ocean"].clone()

                # Generate the sea
                elif (elevation > 0.32) and (elevation < 0.42):
                    if temperature < 0.25:
                        tile = tiles["ice"].clone()
                    else:
                        tile = tiles["water"].clone()

                # Generate the beach
                elif (elevation > 0.42) and (elevation < 0.60):
                    if temperature < 0.25:
                        tile = tiles["snow"].clone()
                    else:
                        tile = tiles["sand"].clone()


                # Generate land biomes
                elif elevation < 1.75:
                    # Cold regions
                    if temperature < 0.25:
                        if humidity < 0.4:
                            # Tundra / Snowlands
                            if randint(0, 8) <= 4:
                                #tile = tiles["frost"].clone()
                                tile = tiles["snow"].clone()
                            else:
                                tile = tiles["snow"].clone()
                        else:
                            # Tundra forest
                            if (elevation > 0.75) and (randint(0, 8) == 4):
                                tile = tiles["pine tree"].clone()
                            else:
                                tile = tiles["snow"].clone()

                    # Cool regions
                    elif temperature < 0.5:
                        if humidity > 0.4:
                            # Plains / Grasslands
                            if (elevation > 0.70) and (randint(0, 8) <= 4):
                                #tile = tiles["tallgrass"].clone()
                                tile = tiles["grass"].clone()
                            else:
                                tile = tiles["grass"].clone() # Snowy grass
                        else:
                            if randint(0, 8) <= 4:
                                #tile = tiles["frost"].clone() # Snowy tallgrass
                                tile = tiles["snow"].clone() # Snowy grass
                            else:
                                tile = tiles["snow"].clone() # Snowy grass

                    # Temperate regions
                    elif temperature < 0.70:
                        if humidity > 0.4:
                            # Temperate forest
                            if (elevation > 0.50) and (randint(0, 8) == 4):
                                tile = tiles["oak tree"].clone()

                    # Warm regions
                    elif temperature < 0.9:
                        if humidity < 0.3:
                            tile = tiles["sand"].clone() # Savanna

                        elif (humidity > 0.3) and (humidity < 0.5):
                            tile = tiles["grass"].clone() # Plains

                        else:
                            if (elevation > 0.60) and (randint(0, 8) == 4):
                                if randint(0, 4) == 2:
                                    tile = tiles["oak tree"].clone()
                                else:
                                    tile = tiles["birch tree"].clone()

                    # Hot regions
                    else:
                        if humidity < 0.4:
                            tile = tiles["sand"].clone() # Desert

                        elif (humidity > 0.4) and (humidity < 0.6):
                            tile = tiles["grass"].clone() # Plains

                        else:
                            if (elevation > 0.60) and (randint(0, 8) == 4):
                                if randint(0, 4) == 2:
                                    tile = tiles["birch tree"].clone()
                                else:
                                    tile = tiles["oak tree"].clone()


                # Generate mountain biomes
                elif elevation < 1.95:
                    tile = tiles["stone"].clone() # Low mountain
                else:
                    tile = tiles["gravel"].clone() # High mountain

                # Add the tile into the chunk
                chunk[h][w] = tile

                # Check for spawnpoint
                if self.sx == 0 and self.sy == 0:
                    if tile.id in { tiles["grass"].id, tiles["sand"].id, tiles["snow"].id }:
                        self.sx = wx
                        self.sy = wy


        self.chunks[(cx, cy)] = chunk


    def get_tile(self, x: int, y: int) -> Tile:
        """ Get the character at coordinates in the world """

        # NOTE: Walrus operators are awesome for performance here ...
        if chunk := self.chunks.get((cx := x // CHUNK_SIZE, cy := y // CHUNK_SIZE)):
            return chunk[y % CHUNK_SIZE][x % CHUNK_SIZE]

        self.load_chunk(cx, cy)
        return self.chunks[(cx, cy)][y % CHUNK_SIZE][x % CHUNK_SIZE]



    def set_tile(self, x: int, y: int, tile: int | Tile) -> None:
        """ Update the world map with the replacement tile """

        # Calculate the chunk coordinates
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE

        # Load the chunk at the calculated chunk coordinates
        self.load_chunk(cx, cy)

        # Calculate the local coordinates within the chunk
        ly = y % CHUNK_SIZE
        lx = x % CHUNK_SIZE

        # Determine the correct Tile object
        if isinstance(tile, int):
            tile = tiles[Game.tile[tile]].clone()
        else:
            tile = tile.clone()

        # Set the tile in the terrain
        self.chunks[(cx, cy)][ly][lx] = tile


    def spawn_mob(self, x: float, y: float, mob: Mob) -> None:
        """ Create and add a new mob to the world """

        # Limit the maximum number of mobs
        if len(self.entities) > 16:
            return

        # We obtain the tile of that position
        tile = self.get_tile(int(x), int(y))

        # We check if the tile is suitable for spawning the mob
        if tile.id in fluids or tile.solid:
            return

        # Assign the position to the mob
        mob.x = x
        mob.y = y

        # We add it to the world
        self.entities.append(mob)


    def despawn_mob(self, x: float, y: float) -> None:
        for mob in self.entities:
            if (int(mob.x) == int(x)) and (int(mob.y) == int(y)):
                self.entities.remove(mob)
                return


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
        for group in self.connectors.values():
            group.clear()

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
                for yt, row in enumerate(chunk):
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
                            tile.connectors = Sprites.get_connector(self, tile, tiles, world_x, world_y)

                        tile.render(self, wx, wy)

        # Sort and render the buffers
        self.depth_buffer.extend(self.player.render(screen))

        for buffer in [
                self.tile_buffer,
                self.connectors['outer'],
                self.connectors['edge'],
                self.connectors['corner'],
                self.depth_buffer,
            ]:
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
                            tiles["dirt"],       # The tile to replace
                            tiles["grass"],      # The tile to replace with

                            # Tiles that can influence the replacement
                            [
                                tiles["grass"],
                                tiles["tallgrass"]
                            ]
                        )

                # Check if it's time to spread water
                if ticks % 8 == 0:
                    self.update_tiles(
                        (cx, cy),            # The chunk to update
                        tiles["hole"],       # The tile to replace
                        tiles["water"],      # The tile to replace with

                        # Tiles that can influence the replacement
                        [
                            tiles["ocean"],
                            tiles["water"]
                        ]
                    )

        """
        if (ticks % 4 == 0):
            for mob in self.entities:
                if randint(0, 8) == 4:
                    mob.move(self)


            if (randint(0, 8) == 4):
                spawn_distance = randint(8, 16) * TILE_SIZE
                angle = randint(0, 359)

                rad_angle = radians(angle)
                cos_angle = cos(rad_angle) * spawn_distance
                sin_angle = sin(rad_angle) * spawn_distance

                if randint(0, 1) == 0:
                    sx = int(self.player.position.x + cos_angle)
                else:
                    sx = int(self.player.position.x - cos_angle)

                if randint(0, 1) == 0:
                    sy = int(self.player.position.y + sin_angle)
                else:
                    sy = int(self.player.position.y - sin_angle)

                if not any((mob.x == sx) and (mob.y == sy) for mob in self.entities):
                    self.spawn_mob(sx, sy, choice([mobs["pig"].clone(), mobs["sheep"].clone()]))
        """


    def update_tiles(self, chunk: tuple, tile_target: Tile, parent: Tile, influences: list) -> None:
        this_chunk = self.chunks.get(chunk)

        if this_chunk:
            target = tile_target.id
            replace = parent.clone()

            # Create a copy of the chunk
            temp_chunk = [
                row[:] for row in this_chunk
            ]

            # Iterate through each tile in the chunk
            for yt in range(CHUNK_SIZE):
                for xt in range(CHUNK_SIZE):

                    # Check if the current tile matches the target tile
                    if this_chunk[yt][xt].id == target:
                        # If influence_tiles is provided, check surrounding tiles
                        if self.tiles_around(chunk, influences, xt, yt):
                            # Replace the target tile with the new tile
                            temp_chunk[yt][xt] = replace

            # Update the terrain with the modified chunk if changes were made
            if temp_chunk != this_chunk:
                self.chunks[chunk] = temp_chunk


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
                if around_chunk[new_y][new_x].id in [tile.id for tile in tiles_around]:
                    return True

        return False
