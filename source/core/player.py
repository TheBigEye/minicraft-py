from __future__ import annotations

from math import hypot
from random import randint
from typing import TYPE_CHECKING

import pygame
from pygame import Vector2

from source.entity.furniture.furniture import Furniture
from source.entity.particle.text import TextParticle

from source.utils.constants import (
    CHUNK_SIZE, SCREEN_HALF_H,
    SCREEN_HALF_W, TILE_SIZE,
    POSITION_SHIFT, TILE_BITS
)

if TYPE_CHECKING:
    from source.screen.screen import Screen
    from source.core.game import Game
    from source.world.tile import Tile
    from source.world.tiles import Tiles
    from source.world.world import World
    from source.screen.sprites import Sprites


class Player:
    def __init__(self, sprites: Sprites, game: Game) -> None:

        self.game: Game = game
        self.tiles: Tiles = None
        self.sprites: Sprites = sprites

        # Player's world coordinates
        self.position: Vector2 = Vector2(0, 0)

        # World grid offset (used by hitbox and tile highlight)
        self.offset: Vector2 = Vector2(0, 0)

        # The direction where the player is facing
        self.facing: Vector2 = Vector2(0, 1)

        # Player's local chunk position
        self.cx: int = 0
        self.cy: int = 0

        # Directions
        self.xd: int = 0
        self.yd: int = 0

        # Player max health, stamina and hunger
        self.MAX_STAT: int = 10

        self.health: int = self.MAX_STAT
        self.energy: int = self.MAX_STAT
        self.hunger: int = self.MAX_STAT

        self.sprite = None
        self.speed = 0
        self.cursor: bool = False
        self.world: World = None



        self.hurt_time: int = 0
        self.swim_time: int = 0

        self.KNOCKBACK: float = 0.35


    def initialize(self, world: World, sx: float, sy: float) -> None:

        self.sprite = self.sprites.PLAYER[1][0]
        self.speed: float = 0.064
        self.world = world

        self.tiles = self.world.tiles

        self.position = Vector2(sx, sy)

        self.cx = int(self.position.x) // CHUNK_SIZE
        self.cy = int(self.position.y) // CHUNK_SIZE


    def swimming(self) -> bool:
        """ Check if the player is swimming """
        # Convert player's position to tile coordinates
        tile_x = int(self.position.x * TILE_BITS) >> POSITION_SHIFT
        tile_y = int(self.position.y * TILE_BITS) >> POSITION_SHIFT

        # Get the tile at the calculated position
        tile: Tile = self.world.get_tile(tile_x, tile_y)
        if not tile:
            return False

        # Return whether the tile is liquid
        return tile.liquid


    def move(self, mx: float, my: float) -> None:

        # NOTE: this code is BLACK MAGIC, i know
        # how this works, but is easy to broke
        # and hard to fix, so i will keep this

        # Calculate deltas in regular coordinates first
        dx = mx - self.position.x
        dy = my - self.position.y

        # In mob.py this is diferent, since that this
        # broke the A.I for some reason, so i will
        # keep this as is, but i will fix the mob.py
        if dx == 0 and dy == 0:
            return

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

        # Check collision
        tile: Tile = self.world.get_tile(tile_x, tile_y)

        if not tile:
            return

        if tile.id == self.tiles.cactus.id:
            self.hurt(1)

        if tile.solid:
            return


        if self.swimming():
            self.swim_time += 1
            if (self.swim_time % 2 == 0):
                return

        if (self.hurt_time > 0):
            return

        # Check if an entity blocks the player movement
        for entity in self.world.entities:
            if isinstance(entity, Furniture):
                if entity.position.distance_to(self.position) < 0.60:
                    entity.touched_by(self)
                    # Only block movement if we're trying to move into the entity's space
                    next_pos = Vector2(self.position.x + dx, self.position.y + dy)
                    if entity.position.distance_to(next_pos) < 0.60:
                        return

        # Store the fractional part to prevent error accumulation (Yeah, sucks)
        self.position.x += dx
        self.position.y += dy

        # Calculate offset for rendering
        self.offset.x = (self.position.x - int(self.position.x)) * TILE_SIZE
        self.offset.y = (self.position.y - int(self.position.y)) * TILE_SIZE

        # Update facing direction
        self.facing = Vector2(dx, dy).normalize()

        self.xd = int(tile_x + self.facing.x)
        self.yd = int(tile_y + self.facing.y)

        # Update chunk position
        self.cx = tile_x // CHUNK_SIZE
        self.cy = tile_y // CHUNK_SIZE


    def attack(self): # type: () -> None
        """ Break the tile in the specified direction """
        if self.energy < int(0.32 * self.MAX_STAT):
            return

        self.energy = max(0, self.energy - int(0.32 * self.MAX_STAT))

        tile: Tile = self.world.get_tile(self.xd, self.yd)
        tile.hurt(self.world, self.xd, self.yd, randint(1, 3))


    def render(self, screen: Screen) -> list:
        sprites = []

        # Tile highlight
        if self.cursor:
            # Calculate highlight position
            tile_x = self.xd - int(self.position.x)
            tile_y = self.yd - int(self.position.y)

            highlight = Vector2(
                (SCREEN_HALF_W + (tile_x * TILE_SIZE)),
                (SCREEN_HALF_H + (tile_y * TILE_SIZE))
            )

            # Adjust for tile offset
            highlight.x -= self.offset.x
            highlight.y -= self.offset.y

            sprites.append((self.sprites.HIGHLIGHT, (highlight.x, highlight.y, highlight.y + 8)))

        screen.darkness.set_alpha(255 - self.world.daylight())

        screen.darkness.blit(
            screen.overlay,
            ((SCREEN_HALF_W - 96), (SCREEN_HALF_H - 92) - 16),
            special_flags=pygame.BLEND_RGBA_SUB
        )


        rx = SCREEN_HALF_W - 15
        ry = SCREEN_HALF_H - 15

        # Player rendering
        if self.swimming():
            half_sprite = self.sprite.subsurface((0, 0, self.sprite.get_width(), self.sprite.get_height() // 2))
            sprites.append((self.sprites.WATER_SWIM[0 if self.cursor else 1], (rx, ry + 2, ry + 2)))
            sprites.append((half_sprite, (rx, ry + 4, ry + 4)))
        else:
            sprites.append((self.sprite, (rx, ry, ry)))

        return sprites


    def update(self, ticks): # type: (int) -> None

        if ticks % 15 == 0:
            # Decrease stamina if we are swimming
            if (self.energy > 0) and self.swimming():
                self.energy = max(0, self.energy - 1)

        # Increase health if stamina is higher than half
        if ticks % 30 == 0:
            if self.energy > (self.MAX_STAT // 2):
                self.health = min(self.MAX_STAT, self.health + 1)

        if (ticks % 30 == 0) and (self.energy < 1):
            if self.swimming():
                self.hurt(1)

        if (ticks % 4 == 0):

            tile: Tile = self.world.get_tile(self.xd, self.yd)
            if tile and tile.solid:
                self.cursor = False
            else:
                self.cursor = not self.cursor

            if not self.swimming() and (self.energy < self.MAX_STAT):
                self.energy = min(self.MAX_STAT, self.energy + 1)

        if (self.hurt_time > 0):
            self.hurt_time -= 1


    def knockback(self, attack_dir: Vector2 = Vector2(0, 0)): # type: (Vector2) -> None
        """ Apply immediate knockback effect when damaged """
        # Use attack_dir if provided, otherwise use opposite of facing direction
        knockback_dir = attack_dir if attack_dir.length() > 0 else -self.facing

        if knockback_dir.length() > 0:
            # Convert current position to bit-shifted coordinates
            current_x = int(self.position.x * TILE_BITS)
            current_y = int(self.position.y * TILE_BITS)

            # Calculate knockback using the determined direction
            knockback_x = int(knockback_dir.x * self.KNOCKBACK * TILE_BITS)
            knockback_y = int(knockback_dir.y * self.KNOCKBACK * TILE_BITS)

            # Calculate new position in bit-shifted coordinates
            new_x = current_x + knockback_x
            new_y = current_y + knockback_y

            # Convert to tile coordinates for collision check
            tile_x = new_x >> POSITION_SHIFT
            tile_y = new_y >> POSITION_SHIFT

            tile: Tile = self.world.get_tile(tile_x, tile_y)

            if not tile.solid:
                # Update position using bit-shifted coordinates
                self.position.x = new_x / TILE_BITS
                self.position.y = new_y / TILE_BITS

                # Update offset for rendering
                self.offset.x = (self.position.x - int(self.position.x)) * TILE_SIZE
                self.offset.y = (self.position.y - int(self.position.y)) * TILE_SIZE

                self.xd = int(tile_x + self.facing.x)
                self.yd = int(tile_y + self.facing.y)

                # Update chunk position
                self.cx = tile_x // CHUNK_SIZE
                self.cy = tile_y // CHUNK_SIZE


    def hurt(self, damage: int, attack_dir: Vector2 = Vector2(0, 0)):
        if (self.hurt_time > 0):
            return

        self.game.sound.play("playerHurt")
        self.world.add(TextParticle(str(damage), self.position.x, self.position.y, (168, 54, 146)))
        self.health = max(0, self.health - damage)

        self.hurt_time = 8

        if not self.swimming():
            self.knockback(attack_dir)
