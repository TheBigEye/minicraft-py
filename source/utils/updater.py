from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from source.game import Game
from source.sound import Sound
from source.utils.saveload import Saveload
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.core.player import Player
    from source.core.world import World


class Updater:

    def __init__(self, world: World, player: Player) -> None:
        self.ticks = 0
        self.timer = 0
        self.world = world
        self.player = player

        # Add cooldown timers
        self.last_shift = 0
        self.last_attack = 0

        self.SHIFT_TIME = 0.5
        self.ATTACK_TIME = 0.05
        self.held_attack = False


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
        dx, dy = 0, 0

        if event[pygame.K_UP] or event[pygame.K_w]:
            dy -= 1
            self.player.sprite = Sprites.PLAYER[0][self.timer]
        if event[pygame.K_DOWN] or event[pygame.K_s]:
            dy += 1
            self.player.sprite = Sprites.PLAYER[1][self.timer]

        if event[pygame.K_LEFT] or event[pygame.K_a]:
            dx -= 1
            self.player.sprite = Sprites.PLAYER[2][self.timer]
        if event[pygame.K_RIGHT] or event[pygame.K_d]:
            dx += 1
            self.player.sprite = Sprites.PLAYER[3][self.timer]


        # Apply swimming slowdown if necessary
        if self.player.swimming():
            dx *= 0.5
            dy *= 0.5

        # Apply movement vector
        if dx != 0 or dy != 0:
            self.player.move(self.player.position.x + dx, self.player.position.y + dy)
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
                    self.last_shift = now

                elif event[pygame.K_r]:
                    self.player.position.x = self.world.sx
                    self.player.position.y = self.world.sy
                    Sound.play("spawnSound")
                    self.last_shift = now


        ## Update world and player
        self.world.update(self.ticks)
        self.player.update(self.ticks)

        # THIS IS IMPORTANT!
        # (If you don't call this, the game will not update)
        self.ticks += 1
