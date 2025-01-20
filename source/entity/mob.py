from __future__ import annotations

from math import hypot
from typing import TYPE_CHECKING

from pygame import Surface, Vector2

from source.core.sound import Sound
from source.entity.brain import Brain, State
from source.entity.entity import Entity
from source.particle.text import TextParticle
from source.screen.color import Color
from source.utils.slots import auto_slots

from source.utils.constants import (
    CHUNK_SIZE, POSITION_SHIFT, SCREEN_FULL_H, SCREEN_FULL_W,
    SCREEN_HALF_H, SCREEN_HALF_W, TILE_BITS, TILE_SIZE
)

if TYPE_CHECKING:
    from source.level.tile import Tile
    from source.level.world import World

@auto_slots
class Mob(Entity):

    def __init__(self):
        super().__init__()

        # Global position
        self.position.x = 0.8
        self.position.y = 0.8

        # Chunk position
        self.cx = 0
        self.cy = 0

        # Screen position
        self.rx = 0
        self.ry = 0

        self.speed: float = 0.060

        self.walk_dist: int = 0
        self.tick_time: int = 0
        self.hurt_time: int = 0
        self.swim_time: int = 0

        self.max_health: int = 10
        self.health: int = self.max_health

        self.last_pos: Vector2 = Vector2(0, 0)

        self.brain: Brain = Brain(self)


    def update(self) -> None:
        self.tick_time += 1

        self.last_pos = Vector2(self.position)

        # Update Mob AI
        if self.brain.state in { State.MOVING, State.CHASING }:
            self.brain.update(self.world)
        elif self.tick_time % 2 == 0:  # For IDLE update each 2 ticks
            self.brain.update(self.world)

        # Update Mob atributes
        if (self.health <= 0):
            self.die()

        if (self.hurt_time > 0):
            self.hurt_time -= 1

        # For sprites rendering ...
        self.rx = int(SCREEN_HALF_W - ((self.world.player.position.x - self.position.x) * TILE_SIZE))
        self.ry = int(SCREEN_HALF_H - ((self.world.player.position.y - self.position.y) * TILE_SIZE))


    def die(self) -> None:
        self.remove()


    def can_swim(self) -> bool:
        return False


    def swimming(self) -> bool:
        tile: Tile = self.world.get_tile(int(self.position.x), int(self.position.y))

        if not tile:
            return False

        if tile.liquid:
            return True

        return False


    def do_hurt(self, damage: int):
        if (self.hurt_time > 0):
            return

        if (self.world.player):
            xd: int = (int(self.world.player.position.x) - int(self.position.x))
            yd: int = (int(self.world.player.position.y) - int(self.position.y))
            if (xd * xd + yd * yd < 80 * 80):
                Sound.play("genericHurt")

        self.world.add(TextParticle(str(damage), self.position.x, self.position.y, Color.DARK_RED))
        self.health -= damage

        self.hurt_time = 15


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

            tile = self.world.get_tile(tile_x, tile_y)

            if not tile:
                return

            if tile.solid:
                return

            if self.swimming():
                self.swim_time += 1
                if (self.swim_time % 2 == 0):
                    return

            if (self.hurt_time > 0):
                return

            self.position.x += dx
            self.position.y += dy

            self.facing = Vector2(dx, dy).normalize()

            # Update chunk position
            self.cx = tile_x // CHUNK_SIZE
            self.cy = tile_y // CHUNK_SIZE

            self.walk_dist += 1



    def render(self, screen: Surface):
        # For avoid append the sprites to the rendering queue
        if not (-TILE_SIZE <= self.rx <= SCREEN_FULL_W and -TILE_SIZE <= self.ry <= SCREEN_FULL_H):
            return
