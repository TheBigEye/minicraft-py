from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from source.world.tile import Tile
    from source.world.tiles import Tiles
    from source.world.world import World


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

    def __init__(self, tiles: Tiles):
        self.tiles = tiles

        self.connections = {}

        self.DIRECTIONS = {
            # X,  Y, Sprite index
            ( 0, -1, 1),  # Top
            ( 1,  0, 2),  # Right
            (-1,  0, 3),  # Left
            ( 0,  1, 4)   # Bottom
        }

        self.OUTER_CORNERS = {
            # X,  Y, Sprite index
            (-1, -1, 5, ('left', 'top')),     # Top-left
            ( 1, -1, 6, ('right', 'top')),    # Top-right
            (-1,  1, 7, ('left', 'bottom')),  # Bottom-left
            ( 1,  1, 8, ('right', 'bottom'))  # Bottom-right
        }

        self.INNER_CORNERS = {
            ( 1,  1, 11, ('right', 'bottom')), # Bottom-right inner
            (-1,  1, 12, ('left', 'bottom')),  # Bottom-left inner
            ( 1, -1, 13, ('right', 'top')),    # Top-right inner
            (-1, -1, 14, ('left', 'top'))      # Top-left inner
        }


    def initialize(self) -> None:
        self.connections = {
            self.tiles.grass.id: {
                self.tiles.grass.id,
                self.tiles.flower.id
            },

            self.tiles.hole.id: {
                self.tiles.hole.id,
                self.tiles.water.id
            },

            self.tiles.sand.id: {
                self.tiles.sand.id,
                self.tiles.cactus.id,
            },

            self.tiles.snow.id: {
                self.tiles.snow.id,
            },

            self.tiles.water.id: {
                self.tiles.water.id,
                self.tiles.iceberg.id,
                self.tiles.ice.id,
                self.tiles.hole.id
            },

            self.tiles.ice.id: {
                self.tiles.ice.id,
                self.tiles.snow.id,
                self.tiles.dirt.id,
            },

            self.tiles.stone.id: {
                self.tiles.stone.id
            }
        }

    # TODO: implement cache for this ... we can reduce the call overheat caching progresivelly each connector sprite

    def connector(self, world: World, tile: Tile, x: int, y: int) -> list:
        """ Get transition sprites for a tile based on its neighbors """
        transitions = []

        if len(tile.sprites) < 9:  # We need at least 9 sprites (base + 4 sides + 4 corners)
            return transitions

        # Get the set of tiles that connect seamlessly with current tile
        connections = self.connections[tile.id]

        # Store which sides have different tiles
        needs_transition = {
            'top': False, 'bottom': False,
            'left': False, 'right': False
        }

        # Store which sides have same tile type
        has_same_type = {
            'top': False, 'bottom': False,
            'left': False, 'right': False
        }

        # Check sides first
        for dx, dy, sprite_index in self.DIRECTIONS:
            neighbor = world.get_tile(x + dx, y + dy)
            # Add transition if neighbor exists and is not in valid connections
            if neighbor:
                if neighbor.id not in connections:
                    transitions.append(tile.sprites[sprite_index])
                    # Mark which sides need transitions
                    if dy == -1: needs_transition['top'] = True
                    elif dy == 1: needs_transition['bottom'] = True
                    elif dx == -1: needs_transition['left'] = True
                    elif dx == 1: needs_transition['right'] = True
                else:
                    # Mark which sides have same type
                    if dy == -1: has_same_type['top'] = True
                    elif dy == 1: has_same_type['bottom'] = True
                    elif dx == -1: has_same_type['left'] = True
                    elif dx == 1: has_same_type['right'] = True

        # Check outer corners if adjacent sides need transitions
        for dx, dy, sprite_index, (side1, side2) in self.OUTER_CORNERS:
            if needs_transition[side1] and needs_transition[side2]:
                neighbor = world.get_tile(x + dx, y + dy)
                if neighbor and neighbor.id not in connections:
                    transitions.append(tile.sprites[sprite_index])

        # Process inner corners if we have enough sprites (14 or more)
        if len(tile.sprites) >= 14:
            for dx, dy, sprite_index, (side1, side2) in self.INNER_CORNERS:
                if has_same_type[side1] and has_same_type[side2]:
                    neighbor = world.get_tile(x + dx, y + dy)
                    if neighbor and neighbor.id not in connections:
                        transitions.append(tile.sprites[sprite_index])

        return transitions
