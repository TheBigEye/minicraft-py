from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Vector2


from source.utils.saveload import Saveload
from source.utils.tests import Tests


if TYPE_CHECKING:
    from source.core.game import Game
    from source.core.player import Player
    from source.world.world import World


class Updater:

    def __init__(self, game: Game) -> None:
        # By default is 3000, so the world starts at evening

        # Used for player sprite
        self.timer: int = 0

        # Used for game independent events
        self.count: int = 0

        # Used for game timing events
        self.ticks: int = 3000

        self.game: Game = game
        self.world: World = game.world
        self.player: Player = game.world.player

        # Add cooldown timers
        self.last_shift: float = 0.00
        self.last_attack: float = 0.00

        self.SHIFT_TIME: float = 0.50
        self.ATTACK_TIME: float = 0.05
        self.held_attack: bool = False

        self.movement = Vector2(0, 0)


    def _cooldown(self, last: float, time: float) -> bool:
        now = pygame.time.get_ticks() / 1000  # Convert to seconds
        return now - last >= time


    def update(self) -> None:
        self.count += 1

        # Check window focus
        #if not pygame.key.get_focused():
        #    Game.focus = False
        #    return
        #else:
        #    Game.focus = True

        # Autosave
        if self.world.loaded and (self.ticks % 1024) == 0:
            Saveload.save(self)

        ### Keyboard input handling ###
        event = pygame.key.get_pressed()

        # Calculate movement vector
        self.movement.update(0, 0)

        if event[pygame.K_UP] or event[pygame.K_w]: self.movement.y -= 1
        if event[pygame.K_DOWN] or event[pygame.K_s]: self.movement.y += 1
        if event[pygame.K_LEFT] or event[pygame.K_a]: self.movement.x -= 1
        if event[pygame.K_RIGHT] or event[pygame.K_d]: self.movement.x += 1


        # Normalize diagonal movement
        if self.movement.length() > 0:
            self.movement.normalize_ip()

            if abs(self.movement.y) > abs(self.movement.x):
                if self.movement.y < 0:
                    self.player.sprite = self.player.sprites.PLAYER[0][self.timer]  # Up
                else:
                    self.player.sprite = self.player.sprites.PLAYER[1][self.timer]  # Down
            else:
                if self.movement.x < 0:
                    self.player.sprite = self.player.sprites.PLAYER[2][self.timer]  # Left
                else:
                    self.player.sprite = self.player.sprites.PLAYER[3][self.timer]  # Right

            # Apply movement vector
            self.player.move(
                self.player.position.x + self.movement.x,
                self.player.position.y + self.movement.y
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
                self.world.debug = not self.world.debug
                self.last_shift = now


        # Handle SHIFT+ combinations
        if event[pygame.K_LSHIFT]:
            now = pygame.time.get_ticks() / 1000

            if self._cooldown(self.last_shift, self.SHIFT_TIME):
                if event[pygame.K_s]:
                    Saveload.save(self)
                    self.game.sound.play("eventSound")

                elif event[pygame.K_g]:
                    Tests.spawn_mobs(self.world, self.player)
                    self.game.sound.play("eventSound")

                elif event[pygame.K_h]:
                    Tests.spawn_furniture(self.world, self.player)
                    self.game.sound.play("eventSound")

                elif event[pygame.K_k]:
                    Tests.clear_mobs(self.world, self.player)
                    self.game.sound.play("eventSound")


                self.last_shift = now


        ## Update world and player
        self.world.update(self.ticks)
        self.player.update(self.ticks)

        # THIS IS IMPORTANT!
        # (If you don't call this, the game will not update)
        self.ticks += 1
