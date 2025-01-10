from __future__ import annotations

from typing import TYPE_CHECKING

from source.level.tile.tiles import Tiles

if TYPE_CHECKING:
    from source.level.tile.tile import Tile
    from source.level.world import World


class Tilemap:
    """ Manages tile transitions using Minicraft's 4-directional system """

    # NOTE: By default, all tiles connect seamlessly with each other. However, by
    # specifying an ID for each tile in CONNECTIONS, we can control which tiles will
    # not connect. For example, if we define "Tiles.grass.id: {Tiles.sand.id}",
    # grass will not connect directly to sand, resulting in a smooth transition
    # effect between the two tile types.

    # This allows the system to manage transitions visually, ensuring that
    # neighboring tiles with different IDs create distinct yet visually appealing
    # transitions instead of abrupt changes.


    # Valid terrain connections
    CONNECTIONS = {

        Tiles.grass.id: {
            Tiles.dirt.id,
            Tiles.sand.id,
            Tiles.snow.id,
            Tiles.water.id,
            Tiles.hole.id,
            Tiles.cactus.id
        },

        Tiles.sand.id: {
            Tiles.dirt.id,
            Tiles.grass.id,
            Tiles.snow.id,
            Tiles.water.id,
            Tiles.hole.id
        },

        Tiles.snow.id: {
            Tiles.dirt.id,
            Tiles.grass.id,
            Tiles.sand.id,
            Tiles.water.id,
            Tiles.hole.id,
            Tiles.cactus.id,
            Tiles.ice.id
        },

        Tiles.water.id: {
            Tiles.dirt.id,
            Tiles.grass.id,
            Tiles.sand.id,
            Tiles.snow.id,
            Tiles.cactus.id,
            Tiles.ice.id
        },

        Tiles.ice.id: {
            Tiles.dirt.id,
            Tiles.snow.id,
            Tiles.water.id,
            Tiles.hole.id,
            Tiles.iceberg.id
        },

        Tiles.hole.id: {
            Tiles.dirt.id,
            Tiles.grass.id,
            Tiles.sand.id,
            Tiles.snow.id,
            Tiles.cactus.id,
            Tiles.ice.id
        }
    }

    @staticmethod
    def connector(world: World, tile: Tile, x: int, y: int) -> list:
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
                transitions.append((tile.sprites[sprite_index]))
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

        for dx, dy, sprite_index, (a, b) in corners:
            if has_transition[a] and has_transition[b]:
                neighbor = world.get_tile(x + dx, y + dy)
                if neighbor.id in valid_neighbors:
                    transitions.append((tile.sprites[sprite_index]))

        return transitions
