from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Font, Surface

from source.screen.screen import Color
from source.utils.constants import *
from source.screen.sprites import Sprites

if TYPE_CHECKING:
    from source.core.world import Player


class Hotbar:

    def __init__(self, player: Player, font: Font) -> None:
        self.font: Font = font
        self.player: Player = player

        self.px: str = ""
        self.py: str = ""

        self.px_pos: tuple = (0, 0)
        self.py_pos: tuple = (0, 0)

        self.bg_color: tuple = (22, 22, 137)

        self.HOTBAR_LENGTH: int = SCREEN_HALF_W // 4
        self.BORDER_HEIGHT: int = SCREEN_FULL_H - 44
        self.HEARTS_HEIGHT: int = SCREEN_FULL_H - 34
        self.STAMINA_HEIGHT: int = SCREEN_FULL_H - 18

        self.BORDERLINE = Sprites.GUI_BORDERLINE
        self.BACKGROUND = Sprites.GUI_BACKGROUND

        self.HEART_NONE = Sprites.HEART_NONE
        self.HEART_FULL = Sprites.HEART_FULL
        self.STAMINA_NONE = Sprites.STAMINA_NONE
        self.STAMINA_FULL = Sprites.STAMINA_FULL

        self.SPRITES = {
            (self.BORDERLINE, self.BORDER_HEIGHT),
            (self.BACKGROUND, self.HEARTS_HEIGHT),
            (self.BACKGROUND, self.STAMINA_HEIGHT),
            (self.BACKGROUND, self.STAMINA_HEIGHT + 2)
        }


    def update(self) -> None:
        self.px = f"X: {self.player.position.x:.2f}"
        self.py = f"Y: {self.player.position.y:.2f}"

        self.px_pos = ((self.HOTBAR_LENGTH * 8) - 32 - (len(self.px) * 8), self.HEARTS_HEIGHT)
        self.py_pos = ((self.HOTBAR_LENGTH * 8) - 32 - (len(self.py) * 8), self.STAMINA_HEIGHT)


    def render(self, screen: Surface) -> None:
        sprites: list = []

        # Render player coordinates
        xp = self.font.render(self.px, False, Color.WHITE, self.bg_color).convert()
        yp = self.font.render(self.py, False, Color.WHITE, self.bg_color).convert()

        # Add the border, background for hearts, and background for stamina
        sprites.extend(
            (sprite[0], (i * 8, sprite[1]))
            for sprite in self.SPRITES
            for i in range(self.HOTBAR_LENGTH)
        )

        # Add coordinates to sprites list
        sprites.append((xp, self.px_pos))
        sprites.append((yp, self.py_pos))

        # Add hearts (full or empty based on player health)
        sprites.extend(
            (self.HEART_FULL if i < self.player.health else self.HEART_NONE, (16 + (i * 16), self.HEARTS_HEIGHT + 1))
            for i in range(self.player.MAX_STAT)
        )

        # Add stamina (full or empty based on player energy)
        sprites.extend(
            (self.STAMINA_FULL if i < self.player.energy else self.STAMINA_NONE, (16 + (i * 16), self.STAMINA_HEIGHT - 1))
            for i in range(self.player.MAX_STAT)
        )

        # Draw all sprites onto the screen
        screen.fblits(sprites)
