from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Set, Tuple

import pygame
from pygame.surface import Surface

from source.utils.constants import *

if TYPE_CHECKING:
    from source.core.tile import Tile
    from source.core.world import World

@staticmethod
def get_sprite(atlas, x, y, step, scale): # type: (Surface, int, int, int, int) -> Surface
    """Extract and scale a sprite from the atlas."""
    return pygame.transform.scale(
        atlas.subsurface((x * step, y * step, step, step)), (scale, scale)
    )

class Sprites:
    """Manages all game sprites and their transitions."""

    # Bitmask constants for terrain connections
    TOP: int = 1 << 0
    BOTTOM: int = 1 << 1
    LEFT: int = 1 << 2
    RIGHT: int = 1 << 3
    TOP_LEFT: int = 1 << 4
    TOP_RIGHT: int = 1 << 5
    BOTTOM_LEFT: int = 1 << 6
    BOTTOM_RIGHT: int = 1 << 7

    # Direction mappings for bitmask calculations
    DIRECTIONS: Set[Tuple[int, int, int]] = {
        ( 0,  1, TOP),
        ( 0, -1, BOTTOM),
        (-1,  0, LEFT),
        ( 1,  0, RIGHT),
        (-1,  1, TOP_LEFT),
        ( 1,  1, TOP_RIGHT),
        (-1, -1, BOTTOM_LEFT),
        ( 1, -1, BOTTOM_RIGHT),
    }

    # Corner and edge definitions
    OUTER_CORNERS: List[Tuple[int, str, Tuple[int, int]]] = [
        (TOP    | RIGHT, "inner_bottom_right", ( TILE_HALF_SIZE, 0)),
        (TOP    | LEFT,  "inner_bottom_left",  (-TILE_HALF_SIZE, 0)),
        (BOTTOM | RIGHT, "inner_top_right",    ( TILE_HALF_SIZE, 0)),
        (BOTTOM | LEFT,  "inner_top_left",     (-TILE_HALF_SIZE, 0))
    ]

    OUTER_EDGES: List[Tuple[int, str, Tuple[int, int]]] = [
        (TOP,    "top",    (0, 0)),
        (BOTTOM, "bottom", (0, 0)),
        (LEFT,   "right",  (-TILE_HALF_SIZE, 0)),
        (RIGHT,  "left",   ( TILE_HALF_SIZE, 0))
    ]

    INNER_CORNERS: List[Tuple[int, str, Tuple[int, int]]] = [
        (TOP_LEFT,     "top_right",    (-TILE_HALF_SIZE, 0)),
        (TOP_RIGHT,    "top_left",     ( TILE_HALF_SIZE, 0)),
        (BOTTOM_LEFT,  "bottom_right", (-TILE_HALF_SIZE, 0)),
        (BOTTOM_RIGHT, "bottom_left",  ( TILE_HALF_SIZE, 0))
    ]

    # Valid terrain connections
    CONNECTIONS: Set[Tuple[str, str]] = {
        ("ice", "snow"),
        ("snow", "sand"),
        ("snow", "grass"),
        ("grass", "sand"),
        ("sand", "water"),
    }

    # Atlas and sprite definitions
    ATLAS: pygame.Surface = pygame.image.load('assets/atlas.png').convert_alpha()

    # Basic sprites
    NULL_TILE = [get_sprite(ATLAS, 0, 31, 16, TILE_SIZE)]
    HIGHLIGHT = get_sprite(ATLAS, 1, 31, 16, TILE_SIZE)

    # UI elements
    HEART_FULL = get_sprite(ATLAS, 4, 62, 8, 16)
    HEART_NONE = get_sprite(ATLAS, 5, 62, 8, 16)
    STAMINA_FULL = get_sprite(ATLAS, 4, 63, 8, 16)
    STAMINA_NONE = get_sprite(ATLAS, 5, 63, 8, 16)
    GUI_BORDERLINE = get_sprite(ATLAS, 7, 62, 8, 16)
    GUI_BACKGROUND = get_sprite(ATLAS, 7, 63, 8, 16)

    # Base terrain sprites
    GRASS = [
        get_sprite(ATLAS, 0, 6, 16, TILE_SIZE),
        get_sprite(ATLAS, 0, 5, 16, TILE_SIZE),
        get_sprite(ATLAS, 0, 4, 16, TILE_SIZE)
    ]

    SAND = [
        get_sprite(ATLAS, 1, 6, 16, TILE_SIZE),
        get_sprite(ATLAS, 1, 5, 16, TILE_SIZE),
    ]

    SNOW = [
        get_sprite(ATLAS, 2, 6, 16, TILE_SIZE),
        get_sprite(ATLAS, 2, 5, 16, TILE_SIZE),
    ]

    ICE = [
        get_sprite(ATLAS, 3, 6, 16, TILE_SIZE),
        get_sprite(ATLAS, 3, 5, 16, TILE_SIZE)
    ]

    ICEBERG = [get_sprite(ATLAS, 3, 4, 16, TILE_SIZE)]
    WATER = [get_sprite(ATLAS, 4, 6, 16, TILE_SIZE)]
    DIRT = [get_sprite(ATLAS, 5, 6, 16, TILE_SIZE)]

    # Tree sprites
    OAK_TREE = [
        get_sprite(ATLAS, 0, 4, 32, TILE_SIZE * 2),
        get_sprite(ATLAS, 1, 4, 32, TILE_SIZE * 2)
    ]

    BIRCH_TREE = [
        get_sprite(ATLAS, 0, 5, 32, TILE_SIZE * 2),
        get_sprite(ATLAS, 1, 5, 32, TILE_SIZE * 2)
    ]

    PINE_TREE = [
        get_sprite(ATLAS, 0, 6, 32, TILE_SIZE * 2),
        get_sprite(ATLAS, 1, 6, 32, TILE_SIZE * 2)
    ]

    # Player sprites [down, left, right, up]
    PLAYER = [
        [get_sprite(ATLAS, 0, 16, 16, TILE_SIZE), get_sprite(ATLAS, 1, 16, 16, TILE_SIZE)],
        [get_sprite(ATLAS, 0, 18, 16, TILE_SIZE), get_sprite(ATLAS, 1, 18, 16, TILE_SIZE)],
        [get_sprite(ATLAS, 0, 17, 16, TILE_SIZE), get_sprite(ATLAS, 1, 17, 16, TILE_SIZE)],
        [get_sprite(ATLAS, 0, 15, 16, TILE_SIZE), get_sprite(ATLAS, 1, 15, 16, TILE_SIZE)],
    ]

    # Transition sprites storage
    transition_sprites: Dict[str, Dict[str, pygame.Surface]] = {}

    @classmethod
    def initialize(cls) -> None:
        """Initialize all transition sprites."""
        TRANSITION_POSITIONS = {
            "grass_sand": ( 0, 0),
            "snow_sand":  ( 3, 0),
            "snow_grass": ( 6, 0),
            "ice_snow":   ( 9, 0),
            "sand_water": (12, 0)
        }

        for transition, (bx, by) in TRANSITION_POSITIONS.items():
            center_terrain = transition.split('_')[0]
            center_sprite = getattr(cls, center_terrain.upper())[1]

            transition_data = {
                "top": get_sprite(cls.ATLAS, bx + 1, by, 16, TILE_SIZE),
                "bottom": get_sprite(cls.ATLAS, bx + 1, by + 2, 16, TILE_SIZE),
                "left": get_sprite(cls.ATLAS, bx, by + 1, 16, TILE_SIZE),
                "right": get_sprite(cls.ATLAS, bx + 2, by + 1, 16, TILE_SIZE),

                "inner_top_left": get_sprite(cls.ATLAS, bx, by, 16, TILE_SIZE),
                "inner_top_right": get_sprite(cls.ATLAS, bx + 2, by, 16, TILE_SIZE),
                "inner_bottom_left": get_sprite(cls.ATLAS, bx, by + 2, 16, TILE_SIZE),
                "inner_bottom_right": get_sprite(cls.ATLAS, bx + 2, by + 2, 16, TILE_SIZE),

                "center": center_sprite,
                "top_left": center_sprite,
                "top_right": center_sprite,
                "bottom_left": center_sprite,
                "bottom_right": center_sprite,
            }

            cls.transition_sprites[transition] = transition_data

            # Create reverse transition mapping
            a, b = transition.split('_')
            cls.transition_sprites[f"{b}_{a}"] = transition_data

    @classmethod
    def get_bitmask(cls, world, x, y, neighbor_id): # type: (World, int, int, int) -> int
        """Calculate the bitmask for terrain transitions."""
        return sum(direction for dx, dy, direction in cls.DIRECTIONS
                  if world.get_tile(x + dx, y + dy).id == neighbor_id)

    @classmethod
    def get_connector(cls, world, tile, tiles, x, y): # type: (World, Tile, dict, int, int) -> list[tuple]
        """Get all connectors for a tile including corners and edges."""
        connectors = []

        for center, neighbor in cls.CONNECTIONS:
            if tile.id != tiles[center].id:
                continue

            bitmask = cls.get_bitmask(world, x, y, tiles[neighbor].id)
            if not bitmask:
                continue

            transition_key = f"{center}_{neighbor}"
            sprites = cls.transition_sprites[transition_key]

            # Check outer corners first
            for mask, corner_name, offset in cls.OUTER_CORNERS:
                if bitmask & mask == mask:
                    return [('outer', sprites[corner_name], offset)]

            # Then check edges
            for direction, sprite_key, offset in cls.OUTER_EDGES:
                if bitmask & direction:
                    return [('edge', sprites[sprite_key], offset)]

            # Finally check inner corners
            for direction, sprite_key, offset in cls.INNER_CORNERS:
                if bitmask & direction:
                    connectors.append(('corner', sprites[sprite_key], offset))

        return connectors

Sprites.initialize()
