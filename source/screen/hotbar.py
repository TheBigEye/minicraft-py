from __future__ import annotations

from typing import TYPE_CHECKING

from source.screen.screen import Screen
from source.screen.sprites import Sprites
from source.utils.constants import SCREEN_SIZE

if TYPE_CHECKING:
    from source.world.world import Player

class Hotbar:

    def __init__(self, sprites: Sprites, player: Player) -> None:
        self.player: Player = player
        self.sprites = sprites

        self.buffer = []

        self.HOTBAR_LENGTH: int = SCREEN_SIZE[0] // 8
        self.BORDER_HEIGHT: int = SCREEN_SIZE[1] - 44
        self.HEARTS_HEIGHT: int = SCREEN_SIZE[1] - 34
        self.STAMINA_HEIGHT: int = SCREEN_SIZE[1] - 18

        self.HEART_NONE = self.sprites.HEART_NONE
        self.HEART_FULL = self.sprites.HEART_FULL
        self.STAMINA_NONE = self.sprites.STAMINA_NONE
        self.STAMINA_FULL = self.sprites.STAMINA_FULL

        self.SPRITES = {
            (self.sprites.GUI[1], self.BORDER_HEIGHT),
            (self.sprites.GUI[0], self.HEARTS_HEIGHT),
            (self.sprites.GUI[0], self.STAMINA_HEIGHT),
            (self.sprites.GUI[0], self.STAMINA_HEIGHT + 2)
        }


    def update(self) -> None:
        pass

    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        # Add the border, background for hearts, and background for stamina
        self.buffer.extend(
            (sprite[0], (i * 8, sprite[1]))
            for sprite in self.SPRITES
            for i in range(self.HOTBAR_LENGTH)
        )

        # Add hearts (full or empty based on player health)
        self.buffer.extend(
            (self.HEART_FULL if i < self.player.health else self.HEART_NONE, (16 + (i * 16), self.HEARTS_HEIGHT))
            for i in range(self.player.MAX_STAT)
        )

        # Add stamina (full or empty based on player energy)
        self.buffer.extend(
            (self.STAMINA_FULL if i < self.player.energy else self.STAMINA_NONE, (16 + (i * 16), self.STAMINA_HEIGHT))
            for i in range(self.player.MAX_STAT)
        )

        # Draw all sprites onto the screen
        screen.buffer.fblits(self.buffer)
