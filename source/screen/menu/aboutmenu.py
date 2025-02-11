from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from source.screen.color import Color
from source.screen.menu.menu import Menu

from source.utils.constants import SCREEN_HALF

if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen


class AboutMenu(Menu):

    def __init__(self, parent: Menu):

        self.parent = parent

        self.MESSAGE = [
            " Minicraft Potato Edition is a remake completely made in ",
            " Python based on the original Minicraft. Developed for   ",
            " me, an Eye :)                                           ",
            "",
            " Minicraft was originally made by Markus Persson (Notch) ",
            " for the ludum dare 22 competition                       ",
            "",
            " Note:                                                   ",
            "  - I sucks at making video games. I prefer making mods  ",
        ]

        self.texts = []
        self.buffer = []


    def initialize(self, game: Game) -> None:
        super().initialize(game)

        self.back: pygame.Surface = pygame.image.load('assets/back2.png').convert()

        title = self.game.screen.font.render(" About ", False, Color.YELLOW, (22, 22, 137)).convert()
        title_rect = title.get_rect(center = (SCREEN_HALF[0], SCREEN_HALF[1] - 168))
        self.texts.append((title, title_rect))

        for i, msg in enumerate(self.MESSAGE):

            shadow = game.screen.font.render(msg, False, Color.BLACK).convert()
            shadow_rect = shadow.get_rect(center = (SCREEN_HALF[0] + 1, 170 + i * 16))
            self.texts.append((shadow, shadow_rect))

            text = game.screen.font.render(msg, False, Color.WHITE, None).convert()
            text_rect = text.get_rect(center = (SCREEN_HALF[0], 170 + i * 16))

            self.texts.append((text, text_rect))


    def update(self) -> None:
        event = pygame.key.get_pressed()

        if event[pygame.K_ESCAPE]:
            self.game.set_menu(self.parent)


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        self.buffer.append((self.back, self.back.get_rect(center = SCREEN_HALF)))

        self.buffer.extend(screen.draw_box(14, 6, 32, 18))
        self.buffer.append((self.game.sprites.GREEN_EYE, self.game.sprites.GREEN_EYE.get_rect(center = (SCREEN_HALF[0], 136))))

        self.buffer.extend(self.texts)

        screen.buffer.blits(self.buffer)
