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
        self.world = world
        self.player = player
        self.timer = 0

    def update(self) -> None:
        event = pygame.key.get_pressed()

        # Calculate movement vector
        dx, dy = 0, 0
        if event[pygame.K_UP]:
            dy -= 1
            self.player.sprite = Sprites.PLAYER[0][self.timer]
        if event[pygame.K_DOWN]:
            dy += 1
            self.player.sprite = Sprites.PLAYER[1][self.timer]

        if event[pygame.K_LEFT]:
            dx -= 1
            self.player.sprite = Sprites.PLAYER[2][self.timer]
        if event[pygame.K_RIGHT]:
            dx += 1
            self.player.sprite = Sprites.PLAYER[3][self.timer]

        # Apply swimming slowdown if necessary
        if self.player.swimming():
            dx *= 0.5
            dy *= 0.5

        if dx != 0 or dy != 0:
            self.player.move(self.player.position.x + dx, self.player.position.y + dy)
            if self.ticks % 6 == 0:
                self.timer = (self.timer + 1) % 2

        if event[pygame.K_c]:
            self.player.attack()

        if event[pygame.K_LSHIFT]:
            # Toggle chunks grid
            if event[pygame.K_g]:
                Game.debug = not Game.debug

            # Save world
            if event[pygame.K_s]:
                Saveload.save(self, self.world, self.player)
                Sound.play("eventSound")

            # Load world
            elif event[pygame.K_l]:
                Saveload.load(self, self.world, self.player)
                Sound.play("eventSound")

            # Move the player to the spawn
            elif event[pygame.K_r]:
                self.player.move(self.world.sx, self.world.sy)
                Sound.play("spawnSound")

        self.world.update(self.ticks)
        self.player.update(self.ticks)

        self.ticks += 1
