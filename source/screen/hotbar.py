from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Font, Surface

from source.screen.color import Color
from source.screen.screen import Screen
from source.utils.constants import SCREEN_HALF_W, SCREEN_FULL_H
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.world.world import Player


class Hotbar:

    def __init__(self, sprites: Sprites, player: Player) -> None:
        self.player: Player = player
        self.sprites = sprites

        self.buffer = []

        self.px: str = ""
        self.py: str = ""

        self.px_pos: tuple = (0, 0)
        self.py_pos: tuple = (0, 0)

        self.bg_color: tuple = (22, 22, 137)

        self.HOTBAR_LENGTH: int = SCREEN_HALF_W // 4
        self.BORDER_HEIGHT: int = SCREEN_FULL_H - 44
        self.HEARTS_HEIGHT: int = SCREEN_FULL_H - 34
        self.STAMINA_HEIGHT: int = SCREEN_FULL_H - 18

        self.BORDERLINE = self.sprites.GUI_TOP_BORDER
        self.BACKGROUND = self.sprites.GUI_BACKGROUND

        self.HEART_NONE = self.sprites.HEART_NONE
        self.HEART_FULL = self.sprites.HEART_FULL
        self.STAMINA_NONE = self.sprites.STAMINA_NONE
        self.STAMINA_FULL = self.sprites.STAMINA_FULL

        self.SPRITES = {
            (self.BORDERLINE, self.BORDER_HEIGHT),
            (self.BACKGROUND, self.HEARTS_HEIGHT),
            (self.BACKGROUND, self.STAMINA_HEIGHT),
            (self.BACKGROUND, self.STAMINA_HEIGHT + 2)
        }


    def update(self) -> None:
        self.px = f"F: ({self.player.facing.x:.0f}, {self.player.facing.y:.0f}), T: {self.player.world.ticks}"
        self.py = f"X: {self.player.position.y:.2f}, Y: {self.player.position.x:.2f}"

        self.px_pos = ((self.HOTBAR_LENGTH * 8) - 32 - (len(self.px) * 8), self.HEARTS_HEIGHT)
        self.py_pos = ((self.HOTBAR_LENGTH * 8) - 32 - (len(self.py) * 8), self.STAMINA_HEIGHT)


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        # Render player coordinates
        xp = screen.font.render(self.px, False, Color.WHITE, self.bg_color).convert()
        yp = screen.font.render(self.py, False, Color.WHITE, self.bg_color).convert()

        # Add the border, background for hearts, and background for stamina
        self.buffer.extend(
            (sprite[0], (i * 8, sprite[1]))
            for sprite in self.SPRITES
            for i in range(self.HOTBAR_LENGTH)
        )

        # Add coordinates to sprites list
        self.buffer.append((xp, self.px_pos))
        self.buffer.append((yp, self.py_pos))

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
