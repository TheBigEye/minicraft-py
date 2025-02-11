from __future__ import annotations

from random import choice, randint, random, seed
from typing import TYPE_CHECKING

from pygame import Vector2
import pygame

from source.entity.entities import Entities

from source.screen.tilemap import Tilemap
from source.utils.region import Region
from source.world.chunk import Chunk
from source.world.generator import Generator
from source.world.noise import Noise

from source.utils.constants import (
    TILE_SIZE, CHUNK_SIZE, RENDER_SIZE,
    SCREEN_HALF, DIRECTIONS
)

if TYPE_CHECKING:
    from source.core.game import Game
    from source.world.tiles import Tiles
    from source.core.player import Player
    from source.entity.entity import Entity
    from source.world.tile import Tile
    from source.screen.sprites import Sprites
    from source.screen.screen import Screen


class World:

    def __init__(self, game: Game, sprites: Sprites, tiles: Tiles, player: Player) -> None:
        # Seed for terrain generation
        self.seed = None
        self.game = game

        self.is_custom = False

        # Permutation matrix for noise generation
        self.perm: list = []

        # Storage for entities and chunks
        self.chunks: dict = {}
        self.entities: list[Entity] = []

        self.ticks: int = 0

        # Spawn point
        self.spawn = Vector2(0.16, 0.16)

        self.player: Player = player
        self.tiles: Tiles = tiles
        self.sprites: Sprites = sprites
        self.loaded: bool = False

        self.generator = Generator(tiles)
        self.tilemap = Tilemap(tiles)

        self.surfaces = []


    def initialize(self, worldseed, populate: bool) -> None:
        """ Initialize the world with a seed and optionally populate it with entities """

        if worldseed == "":
            worldseed = (pygame.time.get_ticks() * randint(-(2**31), 2**31)) // 2

        self.seed = worldseed
        seed(self.seed)

        self.perm = Noise.permutation()

        self.tiles.initialize()
        self.generator.initialize()
        self.tilemap.initialize()

        # Find spawn point before generating chunks
        if self.game.custom.custom_world:
            self.is_custom = True
            self.game.custom.load_tiles(self.game)
            self.spawn = self.game.custom.player_spawn
        else:
            self.spawn = self.generator.find_spawn(self.perm)


        # Calculate spawn chunk coordinates
        cx = int(self.spawn.x) // CHUNK_SIZE
        cy = int(self.spawn.y) // CHUNK_SIZE
        self.load_chunk(cx, cy)

        self.player.initialize(self, self.spawn)

        # Spawn initial mobs
        if populate:
            self.populate()

        self.loaded = True


    def load_chunk(self, cx: int, cy: int) -> None:
        """Load or generate a chunk at the given coordinates."""
        if (cx, cy) in self.chunks:
            return

        if self.is_custom:
            if chunk := self.game.custom.get_chunk(cx, cy):
                self.chunks[(cx, cy)] = chunk
                return
            return

        # Try to load from region file first
        rx, ry, lcx, lcy = Region.get_region(cx, cy)
        region = Region('./saves', rx, ry)
        chunk_data = region.read_chunk(lcx, lcy)

        if chunk_data:
            # Reconstruct chunk from saved data
            chunk_tiles = [
                [self.tiles.get(tile_id).clone() for tile_id in row]
                for row in chunk_data['tiles']
            ]

            chunk: Chunk = Chunk(cx, cy, chunk_tiles)
            chunk.modified = False # Loaded chunks start unmodified

            self.chunks[(cx, cy)] = chunk
            return

        # Generate new chunk
        chunk_tiles = self.generator.make_chunk(cx, cy, self.perm)

        # Set a spawn point
        if self.spawn.x == 0 and self.spawn.y == 0:
            for h in range(CHUNK_SIZE):
                for w in range(CHUNK_SIZE):
                    tile = chunk_tiles[h][w]
                    world_x = cx * CHUNK_SIZE + w
                    world_y = cy * CHUNK_SIZE + h

                    if not tile.solid and not tile.liquid:
                        self.spawn.x = world_x
                        self.spawn.y = world_y
                        break

                if self.spawn.x != 0:
                    break

        self.chunks[(cx, cy)] = Chunk(cx, cy, chunk_tiles)


    def save_chunks(self, center_x: int, center_y: int) -> None:
        """ Save and unload chunks that are too far from the center """

        for (cx, cy) in list(self.chunks.keys()):
            if (abs(cx - center_x) > RENDER_SIZE[0] + 2 or
                abs(cy - center_y) > RENDER_SIZE[1] + 2):

                chunk: Chunk = self.chunks[(cx, cy)]

                if self.is_custom:
                    if chunk.modified:
                        self.game.custom.save_chunk(chunk)
                else:
                    # Save modified chunks before unloading
                    if chunk.modified:
                        rx, ry, lcx, lcy = Region.get_region(cx, cy)
                        save_dir = './mods/saves' if self.game.custom.enabled else './saves'
                        region = Region(save_dir, rx, ry)

                        chunk_data = {
                            'tiles': chunk.data()
                        }

                        region.write_chunk(lcx, lcy, chunk_data)

                del self.chunks[(cx, cy)]


    def get_tile(self, x: int, y: int) -> (Tile | None):
        """ Get a tile at coordinates in the world  """
        if chunk := self.chunks.get((x // CHUNK_SIZE, y // CHUNK_SIZE)):
            return chunk.get(x % CHUNK_SIZE, y % CHUNK_SIZE)
        return None


    def set_tile(self, x: int, y: int, tile: int) -> None:
        """ Set a tile at coordinates in the world """
        # Get chunk coordinates
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE

        # Load chunk if needed
        self.load_chunk(cx, cy)

        # Convert tile ID to Tile object if needed
        tile = self.tiles.get(tile).clone()

        # Get local coordinates within chunk
        lx = x % CHUNK_SIZE
        ly = y % CHUNK_SIZE

        # Update the tile in chunk
        self.chunks[(cx, cy)].set(lx, ly, tile)


    def add(self, entity: Entity) -> None:
        """ Add an entity to the World """
        entity.initialize(self)
        self.entities.append(entity)


    def daylight(self) -> int:
        """ Get the world light value """

        # Dawn: 0-6000 ticks
        # Day: 6000-32000 ticks
        # Dusk: 32000-36000 ticks
        # Night: 36000-48000 ticks

        if self.ticks < 6000:
            return 24 + (self.ticks * 231 // 6000)
        elif self.ticks < 32000:
            return 255
        elif self.ticks < 36000:
            return 255 - ((self.ticks - 32000) * 231 // 4000)
        else:
            return 24


    def render(self, screen: Screen) -> None:
        # Clear draw buffer at start
        self.surfaces.clear()

        # NOTE: All world elements are 2D, positioned using the X and Y axes.
        # They also have a Z axis representing sprite depth, which influences
        # the drawing order.
        # This allows objects to be rendered behind or in front of others.
        # We use a list to store each object's sprite along with a tuple with
        # those values:
        #     [(surface, (x, y, z))]
        #
        # Tiles and entities generally have a Z value of -24. Trees are an
        # exception, typically having a Z value minor to -8.

        # Pre-calculate camera position
        camera_x = int(SCREEN_HALF[0] - (self.player.position.x * TILE_SIZE))
        camera_y = int(SCREEN_HALF[1] - (self.player.position.y * TILE_SIZE))

        # Calculate visible chunk range
        chunk_range = (
            range(self.player.cx - RENDER_SIZE[0] - 1, self.player.cx + RENDER_SIZE[0] + 2),
            range(self.player.cy - RENDER_SIZE[1] - 1, self.player.cy + RENDER_SIZE[1] + 2)
        )

        # Render visible chunks
        for chunk_x in chunk_range[0]:
            for chunk_y in chunk_range[1]:
                # I love walrus operators :)
                if chunk := self.chunks.get((chunk_x, chunk_y)):
                    chunk.render(self, camera_x, camera_y)

        # Add mobs to draw
        for entity in self.entities:
            entity.render(screen)

        # And the player ...
        self.surfaces.extend(self.player.render(screen))

        # Sort and render sprite buffers!
        self.surfaces.sort(key = lambda x: x[1][2])
        screen.buffer.fblits([(sprite, (pos[0], pos[1])) for sprite, pos in self.surfaces])

        # Also render the light dither
        screen.update_light(self.daylight())


    def update(self, ticks) -> None:
        """ Update the world events """

        self.ticks = ticks % 48000

        rx = range(self.player.cx - 4, self.player.cx + 4)
        ry = range(self.player.cy - 3, self.player.cy + 3)

        # Load and update chunks
        for cx in rx:
            for cy in ry:
                self.load_chunk(cx, cy)
                self.update_chunk(cx, cy)

        # Update mobs
        for entity in self.entities:
            entity.update()

        if ticks % 512 == 0:
            # Unload distant chunks
            self.save_chunks(self.player.cx, self.player.cy)


    def update_chunk(self, cx: int, cy: int) -> None:
        chunk = self.chunks.get((cx, cy))
        if not chunk:
            return

        # Water spread ...
        if self.ticks % 8 == 0:
            self.update_tiles(
                chunk,                    # The chunk to update
                self.tiles.hole,               # The tile to replace
                self.tiles.water,              # The tile to replace with
                [self.tiles.water, self.tiles.ice]  # Tiles that can influence
            )

        # Grass spread ...
        if self.ticks % 32 == 0:
            if random() < 0.125:  # 1/8 chance
                self.update_tiles(
                    chunk,
                    self.tiles.dirt,
                    self.tiles.grass,
                    [self.tiles.grass, self.tiles.flower]
                )


    def update_tiles(self, chunk: Chunk, target: Tile, parent: Tile, influences: list) -> None:
        replace = parent.clone()
        modified = False

        # Create a copy of the chunk tiles
        temp = chunk.copy()

        # Iterate through each tile in the chunk
        for yt in range(CHUNK_SIZE):
            for xt in range(CHUNK_SIZE):
                # Check if the current tile matches the target tile
                if chunk.get(xt, yt).id == target.id:
                    # If influence_tiles is provided, check surrounding tiles
                    if self.around_tiles(chunk, influences, xt, yt):
                        # Replace the target tile with the new tile
                        temp[yt][xt] = replace
                        modified = True
                        break

        # Update the terrain with the modified chunk if changes were made
        if modified:
            chunk.fill(temp)


    def around_tiles(self, chunk: Chunk, tiles_around: list, x: int, y: int) -> bool:
        """ Check if any of the specified tiles are around the given coordinates """

        # Check each direction for matching tiles
        for dy, dx in DIRECTIONS:
            new_chunk_x = chunk.x + (x + dx) // CHUNK_SIZE
            new_chunk_y = chunk.y + (y + dy) // CHUNK_SIZE

            # Retrieve the adjacent chunk from the terrain
            around_chunk: Chunk = self.chunks.get((new_chunk_x, new_chunk_y))

            # Check if any adjacent tile matches the specified tile types
            if around_chunk:
                new_y = (y + dy) % CHUNK_SIZE
                new_x = (x + dx) % CHUNK_SIZE

                # Check if tile matches any target tile
                if around_chunk.tiles[new_y][new_x].id in { tile.id for tile in tiles_around }:
                    return True

        return False


    def populate(self) -> None:
        """ Spawn initial mobs in the world """

        for _ in range(6):  # Try spawn 6 random mobs
            # Pick random coordinates near spawn
            x = self.spawn.x + randint(-12, 12)
            y = self.spawn.y + randint(-12, 12)

            # Check if spawn location is valid (not in water/solid blocks)
            tile: Tile = self.get_tile(int(x), int(y))
            if tile and not tile.solid and not tile.liquid:

                mob = choice(Entities.pool[0:3])()
                mob.position = Vector2(x, y)

                self.add(mob)
