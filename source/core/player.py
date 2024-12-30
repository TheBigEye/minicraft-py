from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame
from pygame import Rect, Surface, Vector2

from source.core.tile import fluids
from source.game import Game
from source.screen.debug import Debug
from source.sound import Sound
from source.utils.constants import *
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.core.world import World

class Player:
    def __init__(self): # type: () -> None
        self.rect = Rect(
            SCREEN_HALF_W - 12,
            SCREEN_HALF_H - 12,
            TILE_SIZE,
            TILE_SIZE
        )

        # Player's world coordinates
        self.position: Vector2 = Vector2(0.0, 0.0)

        # World grid offset (used by hitbox and tile highlight)
        self.offset: Vector2 = Vector2(0.0, 0.0)

        # The direction where the player is facing
        self.facing: Vector2 = Vector2(0.0, 0.0)

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
        self.speed: float = 0.10


    def initialize(self, world, sx, sy): # type: (World, float, float) -> None
        self.world = world
        self.position = Vector2(sx, sy)


    def swimming(self): # type: () -> bool
        # Check if the player is swimming (in water)
        return self.world.get_tile(int(self.position.x), int(self.position.y)).id in fluids


    def move(self, mx, my): # type: (float, float) -> None
        """ Move the player using vectors """
        target = Vector2(mx, my)

        # Calcular el vector de movimiento
        movement_vector = target - self.position
        if movement_vector.length() > 0:
            movement_vector = movement_vector.normalize() * self.speed

        # Nueva posición del jugador
        new_position = self.position + movement_vector

        # Comprobar colisión en la nueva posición
        tile = self.world.get_tile(int(new_position.x), int(new_position.y))

        if not tile.solid:
            self.position = new_position
        else:
            # Comprobar colisión con el rectángulo del tile
            tile_rect = Rect((new_position.x * TILE_SIZE), (new_position.x * TILE_SIZE), TILE_SIZE, TILE_SIZE)
            if self.rect.colliderect(tile_rect):
                return

        self.offset.x = (self.position.x - int(self.position.x)) * TILE_SIZE
        self.offset.y = (self.position.y - int(self.position.y)) * TILE_SIZE

        self.rect = Rect(
            SCREEN_HALF_W - self.offset.x,
            SCREEN_HALF_H - self.offset.y,
            TILE_SIZE,
            TILE_SIZE
        )

        # Establecer la dirección en la que está mirando
        if movement_vector.length() > 0:
            self.facing = movement_vector.normalize()

        self.xd = int(self.position.x + self.facing.x)
        self.yd = int(self.position.y + self.facing.y)

        # Update the player local chunk position
        self.cx = int(self.position.x) // CHUNK_SIZE
        self.cy = int(self.position.y) // CHUNK_SIZE


    def attack(self): # type: () -> None
        """ Break the tile in the specified direction """
        if self.energy < int(0.32 * self.MAX_STAT):
            return

        self.energy = max(0, self.energy - int(0.32 * self.MAX_STAT))

        for mob in self.world.entities:
            if (int(mob.x) == self.xd) and (int(mob.y) == self.yd):
                mob.hurt(self.world, 8)
                return

        tile = self.world.get_tile(self.xd, self.yd)
        tile.hurt(self.world, self.xd, self.yd, random.randint(1, 3))


    def render(self, screen): # type: (Surface) -> list[tuple[Surface, tuple]]

        # Create a list to hold all the pygame blits
        sprites: list = []

        # Highlight the front tile
        if self.cursor:
            highlight = Vector2(
                SCREEN_HALF_W, SCREEN_HALF_H
            ) + Vector2(
                self.xd - int(self.position.x), self.yd - int(self.position.y)
            ) * TILE_SIZE

            highlight -= self.offset

            sprites.append((Sprites.HIGHLIGHT, (highlight.x, highlight.y)))

            # We add the player light overlay
            Game.darkness.blit(Game.overlay, ((SCREEN_HALF_W - 96), (SCREEN_HALF_H - 92) - 16), special_flags=pygame.BLEND_RGBA_SUB)
            Game.darkness.set_alpha(255 - self.world.daylight())

        # BUG BUG HERE: this fix temporaly the player's hitbox and sprite problem on negative coords
        xo = TILE_SIZE if self.position.x < 0 else 0
        yo = TILE_SIZE if self.position.y < 0 else 0

        ry = (SCREEN_HALF_H + yo) - 24
        sprites.append((self.sprite, ((SCREEN_HALF_W + xo) - 15, ry, ry)))

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
                self.health = max(0, self.health - 1)
                Sound.play("playerHurt")

        if (ticks % 4 == 0) :
            self.cursor = not self.cursor

            if not self.swimming() and (self.energy < self.MAX_STAT):
                self.energy = min(self.MAX_STAT, self.energy + 1)
