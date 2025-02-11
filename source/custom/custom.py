from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame import Surface, Vector2

from source.custom.loader import CustomLoader
from source.screen.sprites import Sprites
from source.utils.constants import CHUNK_SIZE, TILE_SIZE
from source.utils.region import Region
from source.world.chunk import Chunk
from source.world.tile import Tile
from source.world.tiles import Tiles

if TYPE_CHECKING:
    from source.core.game import Game

class Custom:
    """ Custom content manager """

    def __init__(self, sprites: Sprites, tiles: Tiles):
        self.enabled: bool = False

        self.custom_world: bool = False
        self.custom_atlas: bool = False
        self.custom_player: bool = False

        # Check if w ehave mods to load
        self.mods_dir = Path('./mods')
        if not self.mods_dir.exists():
            return

        self.player_spawn: Vector2 = None

        # We tri find and load a manifest.json
        self.manifest = CustomLoader.manifest(self.mods_dir)

        self.mods_saves = self.mods_dir / 'saves'
        self.world_file = self.mods_dir / 'world.png'
        self.atlas_file = self.mods_dir / 'atlas.png'

        self.custom_tiles: dict = {}
        self.tile_registry: dict = {}

        self.tiles = tiles
        self.sprites = sprites

        # Load custom atlas if present
        if self.atlas_file.exists():
            self.enabled = True

            self.backup_atlas: Surface = None

            self._load_atlas()
            self.custom_atlas = True

        # Load custom world if present
        if self.world_file.exists():
            self.enabled = True

            self.world_width: int = 0
            self.world_height: int = 0
            self.world_data: list = None

            self._load_world()

            self.custom_world = True

            if self.manifest:
                # Load custom player if present in manifest
                if 'custom_player' in self.manifest:
                    self._load_player()


    def load_tiles(self, game: Game) -> None:
        """ Initialize custom tiles """

        # NOTE: this neeeds better code, my style sucks LOL

        # We need a manifest.json
        if not self.manifest:
            return

        # And also we need the custom tiles
        if not 'custom_tilemap' in self.manifest:
            return

        print("[CUSTOM] Initializing custom tiles ...")

        # We get the tiles
        tile_data = self.manifest.get('custom_tilemap', {})
        tile_count = 0

        # These field are needed
        required = {
            'name',  # Used for debug
            'id'     # For base tile
        }

        # These fields are optional for base tiles, but required for custom IDs
        optional = {
            'sprites',  # Tile sprites
            'solid',    # If tile is solid
            'liquid',   # If tile is liquid
            'parent',   # Parent tile ID
            'health'    # Tile health
        }

        for hex_color, data in tile_data.items():
            # Validate required fields
            if not required.issubset(data):
                print(f"[CUSTOM] Missing required fields for tile '{hex_color}'")
                continue

            # We validate the color hexadecimal string
            if not (hex_color.startswith('#') and len(hex_color) == 7):
                print(f"[CUSTOM] Invalid color format '{hex_color}' for tile '{data['name']}'!")
                continue

            try:
                int_color = int(hex_color[1:], 16)
            except ValueError:
                print(f"[CUSTOM] Invalid hex value '{hex_color}' for tile '{data['name']}'!")
                continue


            # Get base tile if exists
            try:
                base_tile = self.tiles.get(data['id'])
                is_custom_id = False
            except ValueError:
                base_tile = None
                is_custom_id = True


            # For custom IDs (non-existing base tiles)
            if is_custom_id:
                # Check that all optional fields are present
                if not optional.issubset(data):
                    missing = optional - set(data.keys())
                    print(f"\n[CUSTOM] FATAL ERROR: Custom tile '{data['name']}' with ID {data['id']} is missing required fields: {missing}")
                    print("[CUSTOM] WHY?: When using custom IDs, all optional fields become required\n")
                    game.quit()

                # Validate sprites exist
                if not data['sprites']:
                    print(f"\n[CUSTOM] FATAL ERROR: Custom tile '{data['name']}' with ID {data['id']} has no sprites defined")
                    print("[CUSTOM] WHY?: Custom tiles must have at least one sprite\n")
                    game.quit()


            # Process sprites
            sprites = []
            if 'sprites' in data:
                for coords in data['sprites']:
                    try:
                        if len(coords) == 2:  # [x, y]
                            sprite = self.sprites.get_tiled(coords[0], coords[1], 16)
                        elif len(coords) == 4:  # [x, y, size]
                            sprite = self.sprites.get_tiled(coords[0], coords[1], coords[2])
                        elif len(coords) == 5:  # [x, y, width, height, scale]
                            sprite = self.sprites.get_px(coords[0], coords[1], coords[2], coords[3], TILE_SIZE * coords[4])
                        else:
                            print(f"[CUSTOM] Invalid sprite format for '{data['name']}'")
                            continue
                        sprites.append(sprite)
                    except Exception as e:
                        print(f"[CUSTOM] Sprite error for '{data['name']}': {e}")
                        continue


            # For base tiles, inherit missing properties
            if not is_custom_id:
                if not sprites:
                    sprites = base_tile.sprites

                # Create tile inheriting from base
                tile = Tile(
                    data['id'],
                    sprites,
                    data.get('solid', base_tile.solid),
                    data.get('liquid', base_tile.liquid),
                    data.get('parent', base_tile.parent),
                    data.get('health', base_tile.health)
                )
            else:
                # Create custom tile with provided properties
                tile = Tile(
                    data['id'],
                    sprites,
                    data['solid'],
                    data['liquid'],
                    data['parent'],
                    data['health']
                )

            self.tile_registry[data['id']] = tile
            self.custom_tiles[int_color] = tile.id

            tile_count += 1

        print(f"[CUSTOM] Nice!, {tile_count} custom tiles loaded!")


    def _load_tile(self, color: int) -> int:
        """ Convert color integers to tile IDs """
        # First check custom tiles
        if color in self.custom_tiles:
            return self.custom_tiles[color]

        # Then fall back to default tile mapping using hex values
        default_colors = {
            0x0000FF: self.tiles.water.id,       # Blue for water
            0xE2C363: self.tiles.sand.id,        # Beige for sand
            0x654321: self.tiles.dirt.id,        # Brown for dirt
            0x808080: self.tiles.hole.id,        # Gray for hole
            0x69CC00: self.tiles.grass.id,       # Green for grass
            0xFFFF00: self.tiles.flower.id,      # Yellow for flower
            0x417F00: self.tiles.oak_tree.id,    # Dark green for oak tree
            0x419B00: self.tiles.birch_tree.id,  # Light green for birch tree
            0x41B200: self.tiles.pine_tree.id,   # Medium green for pine tree
            0x565656: self.tiles.stone.id,       # Gray for stone
            0xC8C8FA: self.tiles.ice.id,         # Light blue for ice
            0xFAFAFF: self.tiles.snow.id,        # White for snow
            0xDCDCFF: self.tiles.iceberg.id,     # Very light blue for iceberg
            0x00FF00: self.tiles.cactus.id,      # Bright green for cactus
            0x878787: self.tiles.iron_ore.id     # Dark gray for iron
        }


        return default_colors.get(color, self.tiles.grass.id)  # Default a grass si no coincide


    def _load_world(self) -> None:
        """ Load and parse the custom world PNG file """
        if not self.world_file.exists():
            raise FileNotFoundError("[CUSTOM] Custom World file not found")

        try:
            # Load and convert world image in a single operation
            world = pygame.image.load(str(self.world_file)).convert()

            # Get dimensions
            self.world_width = world.get_width()
            self.world_height = world.get_height()

            # Pre-allocate the list with correct dimensions
            self.world_data = [[0] * self.world_width for _ in range(self.world_height)]

            # Access pixels directly using get_buffer()
            pixels = pygame.surfarray.pixels2d(world)

            # Fill matrix
            for y in range(self.world_height):
                for x in range(self.world_width):
                    color = world.get_at((x, y))
                    # Use more direct bitwise operation
                    self.world_data[y][x] = color.r << 16 | color.g << 8 | color.b

            # Free temporary surface
            del pixels

        except pygame.error as e:
            print(f"[CUSTOM] Error while loading world: {e}")
            raise

        finally:
            # Ensure image is released even if there's an error
            world = None


    def _load_player(self) -> None:
        """ Load custom player settings from manifest """
        try:
            player_data = self.manifest['custom_player']
            if 'spawn' in player_data:
                pos = player_data['spawn']
                if isinstance(pos, list) and len(pos) == 2:
                    self.player_spawn = Vector2(pos[0], pos[1])
                    self.custom_player = True
                else:
                    print("[CUSTOM] Invalid player spawn position format in manifest")

        except (KeyError, ValueError) as e:
            print(f"[CUSTOM] Error loading custom player from manifest: {e}")
            self.custom_player = False


    def _load_atlas(self) -> None:
        """ Load custom sprites atlas """
        try:
            new_atlas = pygame.image.load(str(self.atlas_file)).convert()

            atlas_size = self.sprites.atlas.get_size()

            # Validate atlas dimensions match original
            if new_atlas.get_width() < atlas_size[0] or new_atlas.get_height() < atlas_size[1]:
                raise ValueError("[CUSTOM] Custom atlas cannot be smaller than the original!")

            # We backup the old atlas
            instance = Sprites()
            self.backup_atlas = instance.atlas

            # Update to the new atlas
            self.sprites.atlas = new_atlas
            self.sprites.atlas.set_colorkey((255, 0, 255))
            self.sprites.initialize()

        except (pygame.error, ValueError) as e:
            print(f"Error loading custom atlas: {e}")
            self.custom_atlas = False


    def restore_atlas(self) -> None:
        """ Restore the original game atlas """
        if self.backup_atlas and self.custom_atlas:
            self.sprites.atlas = self.backup_atlas
            self.sprites.initialize()
            self.custom_atlas = False


    def get_chunk(self, cx: int, cy: int) -> Chunk:
        """ Get a chunk from the custom world data """
        if not self.custom_world or not self.world_data:
            return None

        # Calculate chunk bounds in world coordinates
        sx = cx * CHUNK_SIZE
        sy = cy * CHUNK_SIZE

        # Check if chunk is within custom world bounds
        if (sx >= self.world_width) or (sy >= self.world_height):
            return None

        if (sx + CHUNK_SIZE <= 0) or (sy + CHUNK_SIZE <= 0):
            return None

        # Try to load from region file first
        rx, ry, lcx, lcy = Region.get_region(cx, cy)
        region = Region(str(self.mods_saves), rx, ry)
        chunk_data = region.read_chunk(lcx, lcy)

        if chunk_data:
            # Reconstruct chunk from saved data
            chunk_tiles = [
                [self.get_tile(tile_id).clone() for tile_id in row]
                for row in chunk_data['tiles']
            ]

            chunk: Chunk = Chunk(cx, cy, chunk_tiles)
            chunk.modified = False # Loaded chunks start unmodified

            return chunk

        # Create chunk data
        chunk = []
        for y in range(CHUNK_SIZE):
            row = []
            wx = sy + y

            for x in range(CHUNK_SIZE):
                wy = sx + x

                # Get tile ID from world data or use default (grass)
                if (0 <= wx < self.world_height) and (0 <= wy < self.world_width):
                    color_rgb = self.world_data[wx][wy]
                    tile_id = self._load_tile(color_rgb)
                else:
                    tile_id = 4  # Default to grass

                row.append(self.get_tile(tile_id).clone())

            chunk.append(row)

        return Chunk(cx, cy, chunk)


    def save_chunk(self, chunk: Chunk) -> None:
        """ Save a modified chunk """

        if not self.custom_world:
            return

        self.mods_saves.mkdir(exist_ok=True)

        rx, ry, lcx, lcy = Region.get_region(chunk.x, chunk.y)
        region = Region(str(self.mods_saves), rx, ry)

        data = {
            'tiles': chunk.data()
        }

        region.write_chunk(lcx, lcy, data)


    def get_tile(self, identifier: int) -> Tile:
        """ Get a tile by ID, checking custom tiles first """
        if identifier in self.tile_registry:
            return self.tile_registry[identifier]
        return self.tiles.get(identifier)
