from __future__ import annotations

from typing import TYPE_CHECKING
import pygame
from source.screen.color import Color
from source.screen.menu.menu import Menu

from source.utils.constants import SCREEN_HALF

if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen

class SeedMenu(Menu):

    def __init__(self, parent: Menu):

        self.parent = parent

        # Input state
        self.seed_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        self.texts = []
        self.buffer = []

        self.selection = 0
        self.COOLDOWN = 120  # milliseconds


    def initialize(self, game: Game) -> None:
        super().initialize(game)

        self.back: pygame.Surface = pygame.image.load('assets/back2.png').convert()

        seed_text = self.game.screen.font.render(" Enter World Seed ", False, Color.WHITE, (22, 22, 137)).convert()
        seed_rect = seed_text.get_rect(center=(SCREEN_HALF[0], SCREEN_HALF[1] + 24))
        self.texts.append((seed_text, seed_rect))

        self.seed_input_rect = pygame.Rect(SCREEN_HALF[0] - 136, SCREEN_HALF[1] + 23, 272, 40)

        pygame.key.start_text_input()
        pygame.key.set_text_input_rect(self.seed_input_rect)


    def update(self) -> None:

        event = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        # Check for modded game
        if self.game.custom.custom_world:
            self.game.world.initialize(0, False)
            self.game.set_menu(None)

        # Update cursor blink
        self.cursor_timer = (self.cursor_timer + 1) % 8
        if self.cursor_timer == 0:
            self.cursor_visible = not self.cursor_visible

        for e in pygame.event.get():
            if e.type == pygame.TEXTINPUT:
                if (len(self.seed_input) < 32):
                    self.seed_input += e.text
                    self.game.sound.play("typingSound")

        if current_time - self.selection >= self.COOLDOWN:
            if event[pygame.K_RETURN]:
                pygame.key.stop_text_input()
                self.game.sound.play("confirmSound")
                self.game.world.initialize(self.seed_input, True)
                self.game.set_menu(None)
                self.selection = current_time

        if event[pygame.K_BACKSPACE]:
            self.seed_input = self.seed_input[:-1]

        if event[pygame.K_ESCAPE]:
            self.game.set_menu(self.parent)


    def render(self, screen: Screen) -> None:
        self.buffer.clear()

        if self.game.custom.custom_world:
            return

        self.buffer.append((self.back, self.back.get_rect(center = SCREEN_HALF)))
        self.buffer.extend(screen.draw_box(21, 18, 18, 3))

        self.buffer.extend(self.texts)

        # Render input text
        input_text = screen.font.render(
            self.seed_input + ("█" if self.cursor_visible else " "), False, Color.WHITE
        ).convert()
        self.buffer.append((input_text, input_text.get_rect(center=self.seed_input_rect.center)))

        screen.buffer.blits(self.buffer)
