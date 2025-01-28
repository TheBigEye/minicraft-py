from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from source.screen.color import Color
from source.screen.menu.menu import Menu

from source.utils.constants import SCREEN_HALF_H, SCREEN_HALF_W

if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen


class GuideMenu(Menu):

    def __init__(self, parent: Menu):

        self.parent = parent

        self.MESSAGE = [
            " Move your character with arrow keys or WSAD. Press C to ",
            " attack ...                                              ",
            "",
            " The game is still in development ... so there is no an  ",
            " goal yet :(                                             ",
            "",
            " But look the bright side, you can explore an infinite   ",
            " world (and crash the game, LOL)                         ",
            "",
        ]

        self.texts = []
        self.buffer = []


    def initialize(self, game: Game) -> None:
        super().initialize(game)

        title = self.game.screen.font.render(" How To Play ", False, Color.WHITE, (22, 22, 137)).convert()
        title_rect = title.get_rect(center = (SCREEN_HALF_W, SCREEN_HALF_H - 168))
        self.texts.append((title, title_rect))

        for i in range(len(self.MESSAGE)):

            msg = self.MESSAGE[i]
            col = (255, 255, 255)

            shadow = game.screen.font.render(msg, False, (0, 0, 0)).convert()
            shadow_rect = shadow.get_rect(center = (SCREEN_HALF_W + 1, 170 + i * 16))
            self.texts.append((shadow, shadow_rect))

            text = game.screen.font.render(msg, False, col, None).convert()
            text_rect = text.get_rect(center = (SCREEN_HALF_W, 170 + i * 16))

            self.texts.append((text, text_rect))


    def update(self) -> None:
        event = pygame.key.get_pressed()

        if event[pygame.K_ESCAPE]:
            self.game.display(self.parent)


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        self.buffer.extend(screen.draw_box(self.game.sprites, 14, 6, 32, 18))
        self.buffer.append((self.game.sprites.A_POTATOE, self.game.sprites.A_POTATOE.get_rect(center = (SCREEN_HALF_W, 136))))

        self.buffer.extend(self.texts)

        screen.buffer.blits(self.buffer)
