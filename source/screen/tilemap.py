from __future__ import annotations
from typing import TYPE_CHECKING

from source.core.tiles import Tiles

if TYPE_CHECKING:
    from source.core.tile import Tile
    from source.core.world import World

class Tilemap:
    "" "Manages tile transitions using Minicraft's 4-directional system """

    # Valid terrain connections
    CONNECTIONS = {
        Tiles.grass.id: [Tiles.dirt.id, Tiles.sand.id],
        Tiles.sand.id: [Tiles.water.id],
        Tiles.snow.id: [Tiles.grass.id],
        Tiles.ice.id: [Tiles.snow.id],
        Tiles.hole.id: [Tiles.sand.id, Tiles.dirt.id, Tiles.grass.id, Tiles.snow.id]
    }

    @staticmethod
    def get_transitions(world: World, x: int, y: int, tile: Tile) -> list:
        """ Get transition sprites for a tile based on its neighbors """
        if tile.id not in Tilemap.CONNECTIONS:
            return []

        transitions = []
        valid_neighbors = Tilemap.CONNECTIONS[tile.id]

        # Check cardinal directions first
        directions = [
            ( 0, -1, 1),  # Top
            (-1,  0, 2),  # Left
            ( 1,  0, 3),   # Right
            ( 0,  1, 4)    # Bottom
        ]

        # Store which sides have transitions for corner checking
        has_transition = {
            'top': False, 'bottom': False,
            'left': False, 'right': False
        }

        # Check sides first
        for dx, dy, sprite_index in directions:
            neighbor = world.get_tile(x + dx, y + dy)
            if neighbor.id in valid_neighbors:
                transitions.append((tile.sprites[sprite_index], (x, y)))
                # Mark which sides have transitions
                if dy == -1: has_transition['top'] = True
                elif dy == 1: has_transition['bottom'] = True
                elif dx == -1: has_transition['left'] = True
                elif dx == 1: has_transition['right'] = True

        # Check corners only if adjacent sides have transitions
        corners = [
            (-1, -1, 5,  ('left', 'top')),      # Top-left
            ( 1, -1, 6,  ('right', 'top')),      # Top-right
            (-1,  1, 7,  ('left', 'bottom')),    # Bottom-left
            ( 1,  1, 8,  ('right', 'bottom'))     # Bottom-right
        ]

        for dx, dy, sprite_index, (side1, side2) in corners:
            if has_transition[side1] and has_transition[side2]:
                neighbor = world.get_tile(x + dx, y + dy)
                if neighbor.id in valid_neighbors:
                    transitions.append((tile.sprites[sprite_index], (x, y)))

        return transitions

    @staticmethod
    def connector(world: World, tile: Tile, x: int, y: int) -> list:
        """Returns list of transition sprites needed for this tile"""
        return Tilemap.get_transitions(world, x, y, tile)
