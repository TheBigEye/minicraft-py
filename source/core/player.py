from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame
from pygame import Rect, Surface, Vector2

from source.game import Game
from source.level.tile.tiles import Tiles
from source.sound import Sound
from source.screen.sprites import Sprites

from source.utils.constants import (
    CHUNK_SIZE, SCREEN_HALF_H,
    SCREEN_HALF_W, TILE_SIZE,
    POSITION_SHIFT, TILE_BITS
)

if TYPE_CHECKING:
    from source.level.world import World
    from source.level.tile.tile import Tile


class Player:
    def __init__(self): # type: () -> None
        # Player's world coordinates
        self.position: Vector2 = Vector2(0.0, 0.0)

        # World grid offset (used by hitbox and tile highlight)
        self.offset: Vector2 = Vector2(0.0, 0.0)

        # The direction where the player is facing
        self.facing: Vector2 = Vector2(0.0, 1.0)

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

        self.cursor: bool = False
        self.world: World = None

        self.sprite = Sprites.PLAYER[1][0]
        self.speed = 0.08

        self.KNOCKBACK: float = 0.4


    def initialize(self, world, sx, sy):
        self.world = world
        # Convert initial coordinates to bit-shifted system
        self.position = Vector2(sx, sy)


    def swimming(self) -> bool:
        """Check if the player is swimming (in water) """
        tile: Tile = self.world.get_tile(int(self.position.x), int(self.position.y))
        return tile.liquid


    def move(self, mx, my):
        # Convert target movement to bit-shifted system
        target_x = int(mx * TILE_BITS)
        target_y = int(my * TILE_BITS)
        current_x = int(self.position.x * TILE_BITS)
        current_y = int(self.position.y * TILE_BITS)

        # Calculate movement vector in bit-shifted coordinates
        dx = target_x - current_x
        dy = target_y - current_y

        if dx != 0 or dy != 0:
            # Normalize and apply speed
            length = (dx * dx + dy * dy) ** 0.5
            if length > 0:
                # Calculate movement, preserving diagonal movement
                move_x = int((dx / length) * self.speed * TILE_BITS)
                move_y = int((dy / length) * self.speed * TILE_BITS)

                # New position in bit-shifted coordinates
                new_x = current_x + move_x
                new_y = current_y + move_y

                # Convert to tile coordinates
                tile_x = new_x >> POSITION_SHIFT
                tile_y = new_y >> POSITION_SHIFT

                # Check collision
                tile = self.world.get_tile(tile_x, tile_y)

                if tile.id == Tiles.cactus.id:
                    self.hurt(2)

                if not tile.solid:
                    # Update position in bit-shifted coordinates
                    self.position.x = new_x / TILE_BITS
                    self.position.y = new_y / TILE_BITS

                    # Calculate offset for rendering
                    self.offset.x = (self.position.x - int(self.position.x)) * TILE_SIZE
                    self.offset.y = (self.position.y - int(self.position.y)) * TILE_SIZE

                    # Update facing direction
                    if move_x != 0 or move_y != 0:
                        self.facing = Vector2(move_x, move_y).normalize()

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
        tile.hurt(self.world, self.xd, self.yd, random.randint(1, 3))


    def render(self, screen):
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

            sprites.append((Sprites.HIGHLIGHT, (highlight.x, highlight.y)))

            Game.darkness.blit(
                Game.overlay,
                ((SCREEN_HALF_W - 96), (SCREEN_HALF_H - 92) - 16),
                special_flags=pygame.BLEND_RGBA_SUB
            )

            Game.darkness.set_alpha(255 - self.world.daylight())

        rx = SCREEN_HALF_W - 15
        ry = SCREEN_HALF_H - 24

        # Player rendering
        if self.swimming():
            half_sprite = self.sprite.subsurface((0, 0, self.sprite.get_width(), self.sprite.get_height() // 2))
            sprites.append((Sprites.WATER_SWIM[0 if self.cursor else 1], (rx, ry - 8)))
            sprites.append((half_sprite, (rx, ry - 4)))
        else:
            sprites.append((self.sprite, (rx, ry)))

        return sprites


    def update(self, ticks): # type: (int) -> None
        if ticks % 15 == 0:
            # Decrease stamina if we are swimming
            if (self.energy > 0) and self.swimming():
                self.energy = max(0, self.energy - 1)

            # Increase health if stamina is higher than half
            if self.energy > (self.MAX_STAT // 2):
                self.health = min(self.MAX_STAT, self.health + 1)

        if (ticks % 30 == 0) and (self.energy < 1):
            if self.swimming():
                self.hurt(1)

        if (ticks % 4 == 0):
            self.cursor = not self.cursor

            if not self.swimming() and (self.energy < self.MAX_STAT):
                self.energy = min(self.MAX_STAT, self.energy + 1)


    def knockback(self): # type: () -> None
        """ Apply immediate knockback effect when damaged """
        if self.facing.length() > 0:
            # Convert current position to bit-shifted coordinates
            current_x = int(self.position.x * TILE_BITS)
            current_y = int(self.position.y * TILE_BITS)

            # Calculate knockback direction (opposite to facing direction)
            knockback_x = -int(self.facing.x * self.KNOCKBACK * TILE_BITS)
            knockback_y = -int(self.facing.y * self.KNOCKBACK * TILE_BITS)

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

                # Update chunk position
                self.cx = tile_x // CHUNK_SIZE
                self.cy = tile_y // CHUNK_SIZE


    def hurt(self, damage: int):
        self.health = max(0, self.health - damage)
        self.knockback()
        Sound.play("playerHurt")
