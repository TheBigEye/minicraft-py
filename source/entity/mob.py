from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Surface, Vector2

from source.entity.brain import HostileBrain, PassiveBrain, State
from source.level.tile.tile import Tile
from source.utils.constants import CHUNK_SIZE, POSITION_SHIFT, TILE_BITS

if TYPE_CHECKING:
    from source.level.world import World


class Mob:
    __slots__ = [
        'id', 'sprite', 'sprites', 'health', 'speed',
        'hostile', 'frame', 'timer', 'last_pos',
        'position', 'facing', 'brain', 'cx', 'cy'
    ]

    def __init__(self, id: int, sprites: list[Surface], health: int, speed: float, hostile: bool = False):
        self.id = id
        self.sprites = sprites
        self.health = health
        self.speed = speed
        self.hostile = hostile

        self.position: Vector2 = Vector2(0, 0)
        self.facing: Vector2 = Vector2(0, 1)

        # Mob local chunk position
        self.cx: int = 0
        self.cy: int = 0

        # Animation state
        self.frame = 0
        self.timer = 0
        self.last_pos = Vector2(0, 0)

        # Set initial sprite (facing down)
        self.sprite = self.sprites[1][0]

        self.brain = HostileBrain(self) if hostile else PassiveBrain(self)

    def move(self, world: World, target_x: float, target_y: float) -> None:
        """Move the mob towards a target position using grid-based movement"""
        # Convert current and target positions to tile coordinates
        current_tile_x = int(self.position.x)
        current_tile_y = int(self.position.y)
        target_tile_x = int(target_x)
        target_tile_y = int(target_y)

        # Calculate direction to move (ensure we only move in cardinal directions)
        dx = target_tile_x - current_tile_x
        dy = target_tile_y - current_tile_y

        # Determine the primary direction to move (only one direction at a time)
        move_x = 0
        move_y = 0

        # Prioritize the larger difference
        if abs(dx) > abs(dy):
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
        else:
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0

        # Calculate new position
        new_x = self.position.x + move_x * self.speed
        new_y = self.position.y + move_y * self.speed

        # Check if the new position is valid
        new_tile_x = int(new_x)
        new_tile_y = int(new_y)

        tile = world.get_tile(new_tile_x, new_tile_y)

        if not tile.solid and not tile.liquid:
            # Update position
            self.position.x = new_x
            self.position.y = new_y

            # Update facing direction
            if move_x != 0 or move_y != 0:
                self.facing = Vector2(move_x, move_y)

            # Update chunk position
            self.cx = new_tile_x // CHUNK_SIZE
            self.cy = new_tile_y // CHUNK_SIZE


    def update(self, ticks: int, world: World) -> None:
        # Update brain
        if ticks % 2 == 0:
            self.brain.update(world)

        # Store last position for animation
        self.last_pos = Vector2(self.position)

        # Update movement if in a moving state
        if self.brain.state in {State.MOVING, State.CHASING}:
            self.brain.update(world)

        # Update animation timer
        if ticks % 6 == 0 and self.position != self.last_pos:
            self.timer = (self.timer + 1) % 2

        self.update_sprite()

    def update_sprite(self) -> None:
        """Update sprite based on movement direction"""
        movement = self.position - self.last_pos

        if movement.length() > 0:
            # Determine sprite direction based on movement
            if abs(movement.x) > abs(movement.y):
                sprite_row = 3 if movement.x > 0 else 2  # Right or Left
                self.facing = Vector2(1, 0) if movement.x > 0 else Vector2(-1, 0)
            else:
                sprite_row = 1 if movement.y > 0 else 0  # Down or Up
                self.facing = Vector2(0, 1) if movement.y > 0 else Vector2(0, -1)

            self.sprite = self.sprites[sprite_row][self.timer]
        else:
            # Use standing sprite based on last facing direction
            if self.facing.y < 0:
                self.sprite = self.sprites[0][0]  # Up
            elif self.facing.y > 0:
                self.sprite = self.sprites[1][0]  # Down
            elif self.facing.x < 0:
                self.sprite = self.sprites[2][0]  # Left
            else:
                self.sprite = self.sprites[3][0]  # Right

    def clone(self) -> Mob:
        """Create a new instance of this mob"""
        return self.__class__(self.id, self.sprites, self.health, self.speed, self.hostile)
