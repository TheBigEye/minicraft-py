from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Vector2

from source.core.game import Game
from source.core.sound import Sound
from source.screen.sprites import Sprites
from source.utils.saveload import Saveload
from source.utils.tests import Tests

if TYPE_CHECKING:
    from source.core.player import Player
    from source.level.world import World


class Updater:

    def __init__(self, world: World, player: Player) -> None:
        # By default is 3000, so the world starts at evening

        self.timer: int = 0
        self.ticks: int = 3000
        self.world: World = world
        self.player: Player = player

        # Add cooldown timers
        self.last_shift: float = 0.00
        self.last_attack: float = 0.00

        self.SHIFT_TIME: float = 0.50
        self.ATTACK_TIME: float = 0.05
        self.held_attack: bool = False

        try:
            Saveload.load(self, self.world, self.player)
        except FileNotFoundError:
            world.loaded = False


    def _cooldown(self, last: float, time: float) -> bool:
        now = pygame.time.get_ticks() / 1000  # Convert to seconds
        return now - last >= time


    def update(self) -> None:
        # Autosave
        if self.world.loaded and (self.ticks % 1024) == 0:
            Saveload.save(self, self.world, self.player)

        ### Keyboard input handling ###
        event = pygame.key.get_pressed()

        # Calculate movement vector
        movement = Vector2(0, 0)

        if event[pygame.K_UP] or event[pygame.K_w]:
            movement.y -= 1
        if event[pygame.K_DOWN] or event[pygame.K_s]:
            movement.y += 1

        if event[pygame.K_LEFT] or event[pygame.K_a]:
            movement.x -= 1
        if event[pygame.K_RIGHT] or event[pygame.K_d]:
            movement.x += 1


        # Normalize diagonal movement
        if movement.length() > 0:
            movement = movement.normalize()

            if abs(movement.y) > abs(movement.x):
                if movement.y < 0:
                    self.player.sprite = Sprites.PLAYER[0][self.timer]  # Up
                else:
                    self.player.sprite = Sprites.PLAYER[1][self.timer]  # Down
            else:
                if movement.x < 0:
                    self.player.sprite = Sprites.PLAYER[2][self.timer]  # Left
                else:
                    self.player.sprite = Sprites.PLAYER[3][self.timer]  # Right

            # Apply movement vector
            self.player.move(
                self.player.position.x + movement.x,
                self.player.position.y + movement.y
            )

            # Update player sprite animation
            if self.ticks % 6 == 0:
                self.timer = (self.timer + 1) % 2


        # Handle attack (press-release check)
        if event[pygame.K_c]:
            if not self.held_attack and self._cooldown(self.last_attack, self.ATTACK_TIME):
                self.player.attack()
                self.last_attack = pygame.time.get_ticks() / 1000
            self.held_attack = True
        else:
            self.held_attack = False


        # Handle F3 debug toggle
        if event[pygame.K_F3]:
            now = pygame.time.get_ticks() / 1000

            if self._cooldown(self.last_shift, self.SHIFT_TIME):
                Game.debug = not Game.debug
                self.last_shift = now


        # Handle SHIFT+ combinations
        if event[pygame.K_LSHIFT]:
            now = pygame.time.get_ticks() / 1000

            if self._cooldown(self.last_shift, self.SHIFT_TIME):
                if event[pygame.K_s]:
                    Saveload.save(self, self.world, self.player)
                    Sound.play("eventSound")

                elif event[pygame.K_g]:
                    Tests.spawn_mobs(self.world, self.player)
                    Sound.play("eventSound")

                self.last_shift = now


        ## Update world and player
        self.world.update(self.ticks)
        self.player.update(self.ticks)

        # THIS IS IMPORTANT!
        # (If you don't call this, the game will not update)
        self.ticks += 1
