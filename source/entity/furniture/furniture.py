from __future__ import annotations

from math import hypot
from typing import TYPE_CHECKING

from pygame import Surface, Vector2
from source.entity.entity import Entity

from source.utils.constants import (
    CHUNK_SIZE, POSITION_SHIFT, SCREEN_HEIGHT,
    SCREEN_WIDTH, SCREEN_HALF_H, SCREEN_HALF_W,
    TILE_BITS, TILE_SIZE
)

from source.utils.autoslots import auto_slots

if TYPE_CHECKING:
    from source.core.player import Player
    from source.world.world import World

@auto_slots
class Furniture(Entity):

    def __init__(self, name: str):
        super().__init__()

        self.eid = -1

        self.name: str = name
        self.should_take: Player = None
        self.push_time: int = 0
        self.push_dir: Vector2 = Vector2(0, 0)

        self.position.x = 0.80
        self.position.y = 0.80

        self.speed = 0.080

        self.cx = 0
        self.cy = 0

        self.rx = 0
        self.ry = 0


    def move(self, world: World, mx: float, my: float) -> None:
        """ Move the mob towards a target position using grid-based movement """
        # Convert current and target positions to tile coordinates
        dx = mx - self.position.x
        dy = my - self.position.y

        if dx != 0 or dy != 0:
            # Normalize the movement vector and apply speed uniformly
            length = hypot(dx, dy)
            if length > 0:
                dx = (dx / length) * self.speed
                dy = (dy / length) * self.speed

            # Convert movement to bit-shifted format
            new_x = int((self.position.x + dx) * TILE_BITS)
            new_y = int((self.position.y + dy) * TILE_BITS)

            # Convert to tile coordinates for collision
            tile_x = new_x >> POSITION_SHIFT
            tile_y = new_y >> POSITION_SHIFT

            # Get current tile position
            current_x = int(self.position.x)
            current_y = int(self.position.y)

            # For diagonal movement, check both intermediate tiles
            if current_x != tile_x and current_y != tile_y:
                # Check horizontal movement
                tile_h = world.get_tile(tile_x, current_y)
                if not tile_h or tile_h.solid or tile_h.liquid:
                    dx = 0  # Block horizontal movement

                # Check vertical movement
                tile_v = world.get_tile(current_x, tile_y)
                if not tile_v or tile_v.solid or tile_v.liquid:
                    dy = 0  # Block vertical movement

            # Check final tile
            tile = world.get_tile(tile_x, tile_y)

            # If the tile doesnt exist ...
            if not tile:
                return # We dont move

            # If the tile is solid or liquid ...
            if tile.solid or tile.liquid:
                return # We dont move

            # Now yes, we move (if there's any movement left)
            if dx != 0 or dy != 0:
                self.position.x += dx
                self.position.y += dy

                self.facing = Vector2(dx, dy).normalize()

                # Update chunk position
                self.cx = tile_x // CHUNK_SIZE
                self.cy = tile_y // CHUNK_SIZE


    def update(self):
        if self.push_time > 0:
            # Move in the direction of push_dir
            target_x = self.position.x + self.push_dir.x
            target_y = self.position.y + self.push_dir.y
            self.move(self.world, target_x, target_y)

            self.push_dir = Vector2(0, 0)
            self.push_time -= 1

        self.rx = int(SCREEN_HALF_W - ((self.world.player.position.x - self.position.x) * TILE_SIZE))
        self.ry = int(SCREEN_HALF_H - ((self.world.player.position.y - self.position.y) * TILE_SIZE))


    def touched_by(self, player: Player):
        if (self.push_time == 0):
            self.push_dir = player.facing
            self.push_time = 10


    def take(self, player: Player):
        self.should_take = player


    def render(self, screen: Surface):
        if not (-TILE_SIZE <= self.rx <= SCREEN_WIDTH and -TILE_SIZE <= self.ry <= SCREEN_HEIGHT):
            return
