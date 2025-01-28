from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from source.screen.color import Color
from source.screen.menu.menu import Menu

from source.utils.constants import SCREEN_HALF_H, SCREEN_HALF_W

if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen


class AboutMenu(Menu):

    def __init__(self, parent: Menu):

        self.parent = parent

        self.MESSAGE = [
            " Minicraft Potato Edition is a remake completely made in ",
            " Python based on the original Minicraft, developed for   ",
            " me, an Eye :)                                           ",
            "",
            " Minicraft was originally made by Markus Persson (Notch) ",
            " for the ludum dare 22 competition                       ",
            "",
            " Note:                                                   ",
            "  - I suck at making video games, I prefer making mods   ",
        ]

        self.texts = []
        self.buffer = []


    def initialize(self, game: Game) -> None:
        super().initialize(game)

        title = self.game.screen.font.render(" About ", False, Color.WHITE, (22, 22, 137)).convert()
        title_rect = title.get_rect(center=(SCREEN_HALF_W, SCREEN_HALF_H - 168))
        self.texts.append((title, title_rect))

        for i in range(len(self.MESSAGE)):

            msg = self.MESSAGE[i]
            col = (255, 255, 255)

            shadow = game.screen.font.render(msg, False, (0, 0, 0)).convert()
            shadow_rect = shadow.get_rect(center=(SCREEN_HALF_W + 1, 170 + i * 16))
            self.texts.append((shadow, shadow_rect))

            text = game.screen.font.render(msg, False, col, None).convert()
            text_rect = text.get_rect(center=(SCREEN_HALF_W, 170 + i * 16))

            self.texts.append((text, text_rect))



    def update(self) -> None:
        event = pygame.key.get_pressed()

        if event[pygame.K_ESCAPE]:
            self.game.display(self.parent)


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        self.buffer.extend(screen.draw_box(self.game.sprites, 14, 6, 32, 18))
        self.buffer.append((self.game.sprites.GREEN_EYE, self.game.sprites.GREEN_EYE.get_rect(center = (SCREEN_HALF_W, 136))))

        self.buffer.extend(self.texts)

        screen.buffer.blits(self.buffer)
