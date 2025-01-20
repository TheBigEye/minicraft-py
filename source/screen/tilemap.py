from __future__ import annotations

from typing import TYPE_CHECKING

from source.level.tiles import Tiles

if TYPE_CHECKING:
    from source.level.tile import Tile
    from source.level.world import World


class Tilemap:
    """ Manages tile transitions using Minicraft's 4-directional system """

    # NOTE: By default, tiles DO NOT connect seamlessly with each other resulting in a
    # smooth transition effect between the two tile types. However, by specifying an ID
    # for each tile in CONNECTIONS, we can control which tiles WILL connect.
    # For example, if we define "Tiles.grass.id: {Tiles.flower.id}", grass will connect
    # directly to flower

    # This allows the system to manage transitions visually, ensuring that
    # neighboring tiles with different IDs create distinct yet visually appealing
    # transitions instead of abrupt changes.

    # Valid terrain connections
    CONNECTIONS = {

        Tiles.grass.id: {
            Tiles.grass.id
        },

        Tiles.hole.id: {
            Tiles.hole.id,
            Tiles.water.id
        },

        Tiles.sand.id: {
            Tiles.sand.id,
            Tiles.cactus.id,
        },

        Tiles.snow.id: {
            Tiles.snow.id,
        },

        Tiles.water.id: {
            Tiles.water.id,
            Tiles.iceberg.id,
            Tiles.ice.id,
            Tiles.hole.id
        },

        Tiles.ice.id: {
            Tiles.ice.id,
            Tiles.snow.id,
            Tiles.dirt.id,
        },

        Tiles.stone.id: {
            Tiles.stone.id
        }
    }

    @staticmethod
    def connector(world: World, tile: Tile, x: int, y: int) -> list:
        """ Get transition sprites for a tile based on its neighbors """
        transitions = []

        if len(tile.sprites) < 9:  # We need at least 9 sprites (base + 4 sides + 4 corners)
            return transitions

        # Get the set of tiles that connect seamlessly with current tile
        valid_connections = Tilemap.CONNECTIONS[tile.id]

        # Check cardinal directions first
        directions = [
            ( 0, -1, 1),  # Top
            (-1,  0, 2),  # Left
            ( 1,  0, 3),  # Right
            ( 0,  1, 4)   # Bottom
        ]

        # Store which sides need transitions
        needs_transition = {
            'top': False, 'bottom': False,
            'left': False, 'right': False
        }

        # Check sides first
        for dx, dy, sprite_index in directions:
            neighbor = world.get_tile(x + dx, y + dy)
            # Add transition if neighbor exists and is not in valid connections
            if neighbor and neighbor.id not in valid_connections:
                transitions.append(tile.sprites[sprite_index])
                # Mark which sides need transitions
                if dy == -1:
                    needs_transition['top'] = True
                elif dy == 1:
                    needs_transition['bottom'] = True
                elif dx == -1:
                    needs_transition['left'] = True
                elif dx == 1:
                    needs_transition['right'] = True

        # Check corners only if adjacent sides need transitions
        corners = [
            (-1, -1, 5, ('left', 'top')),     # Top-left
            ( 1, -1, 6, ('right', 'top')),    # Top-right
            (-1,  1, 7, ('left', 'bottom')),  # Bottom-left
            ( 1,  1, 8, ('right', 'bottom'))  # Bottom-right
        ]

        for dx, dy, sprite_index, (a, b) in corners:
            if needs_transition[a] and needs_transition[b]:
                neighbor = world.get_tile(x + dx, y + dy)
                if neighbor and neighbor.id not in valid_connections:
                    transitions.append(tile.sprites[sprite_index])

        return transitions
