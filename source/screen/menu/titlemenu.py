from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from pygame import Surface

from source.screen.color import Color
from source.screen.menu.aboutmenu import AboutMenu
from source.screen.menu.guidemenu import GuideMenu
from source.screen.menu.menu import Menu
from source.screen.menu.seedmenu import SeedMenu

from source.utils.constants import (
    SCREEN_FULL_H, SCREEN_FULL_W,
    SCREEN_HALF_H, SCREEN_HALF_W
)

from source.utils.saveload import Saveload

if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen


class TitleMenu(Menu):

    def __init__(self):
        self.selected = 0
        self.OPTIONS = [
            "Start game",   # 0
            "How to play",  # 1
            "About"         # 2
        ]

        self.texts = []
        self.buffer = []

        self.selection = 0
        self.COOLDOWN = 120  # milliseconds


    def initialize(self, game: Game) -> None:
        super().initialize(game)

        pygame.mixer.music.load('./assets/sounds/titleTheme.ogg')
        pygame.mixer.music.set_volume(0.32)
        pygame.mixer.music.play(-1, fade_ms=10000)

        self.title: Surface = pygame.transform.scale(
            pygame.image.load('assets/title.png').convert(), (104 * 4.4, 16 * 4.4)
        )

        self.title.set_colorkey((255, 0, 255))

        # Background image scaled by 2x
        self.back: Surface = pygame.transform.scale(
            pygame.image.load('assets/back.png').convert(), (384 * 2.5, 216 * 2.5)
        )

        # Edition Text with shadow
        edition_text = "════════════════ Potato Edition ════════════════"

        # Shadow text
        shadow = game.screen.font.render(edition_text, False, (27, 45, 32)).convert()
        shadow_rect = shadow.get_rect(center=(SCREEN_HALF_W + 1, SCREEN_HALF_H - 59))

        # Main text
        text = game.screen.font.render(edition_text, False, (137, 229, 160)).convert()
        text_rect = text.get_rect(center=(SCREEN_HALF_W, SCREEN_HALF_H - 60))

        # Add both to the texts list
        self.texts.extend([(shadow, shadow_rect), (text, text_rect)])

        # Author text
        author_text = game.screen.font.render("Game by TheBigEye", False, Color.GRAY).convert()
        author_rect = author_text.get_rect(bottomleft=(4, SCREEN_FULL_H))
        self.texts.append((author_text, author_rect))

        # Version text
        version_text = game.screen.font.render("Infdev 1.0a", False, Color.GRAY).convert()
        version_rect = version_text.get_rect(bottomright=(SCREEN_FULL_W - 4, SCREEN_FULL_H))
        self.texts.append((version_text, version_rect))


    def update(self) -> None:
        event = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Check if enough time has passed since last selection
        if current_time - self.selection >= self.COOLDOWN:
            if event[pygame.K_UP]:
                self.selected = (self.selected - 1) % len(self.OPTIONS)
                self.game.sound.play("typingSound")
                self.selection = current_time
            elif event[pygame.K_DOWN]:
                self.selected = (self.selected + 1) % len(self.OPTIONS)
                self.game.sound.play("typingSound")
                self.selection = current_time

        if event[pygame.K_RETURN]:

            pygame.mixer.music.fadeout(1500)
            pygame.mixer.music.unload()

            if self.selected == 0:

                try:
                    Saveload.load(self.game.updater)
                    self.game.sound.play("eventSound")
                    self.game.display(None)

                except FileNotFoundError:
                    self.game.world.loaded = False
                    self.game.display(SeedMenu(self))

            elif self.selected == 1:
                self.game.display(GuideMenu(self))
            elif self.selected == 2:
                self.game.display(AboutMenu(self))

            self.game.sound.play("confirmSound")


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        self.buffer.append((self.back, self.back.get_rect(center = (SCREEN_HALF_W, 270))))
        self.buffer.append((self.title, self.title.get_rect(center = (SCREEN_HALF_W, 160))))

        self.buffer.extend(screen.draw_box(self.game.sprites, 24, 16, 12, 5))

        for i in range(len(self.OPTIONS)):
            msg = self.OPTIONS[i]
            col = (128, 128, 128)

            if i == self.selected:
                msg = "> " + msg + " <"
                col = (255, 255, 255)

            shadow = screen.font.render(msg, False, (0, 0, 0)).convert()
            shadow_rect = shadow.get_rect(center=(SCREEN_HALF_W + 1, 280 + i * 16))
            self.buffer.append((shadow, shadow_rect))

            text = screen.font.render(msg, False, col, None).convert()
            text_rect = text.get_rect(center=(SCREEN_HALF_W, 280 + i * 16))

            self.buffer.append((text, text_rect))

        self.buffer.extend(self.texts)

        screen.buffer.blits(self.buffer)
