from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

import pygame
from pygame import Font, Surface

from source.screen.screen import Color, Screen
from source.sound import Sound

from source.utils.constants import (
    SCREEN_FULL_H, SCREEN_FULL_W,
    SCREEN_HALF_H, SCREEN_HALF_W,
    SCREEN_SIZE_T
)

if TYPE_CHECKING:
    from source.level.world import World


class StartMenu:
    def __init__(self, world: World, font: Font) -> None:
        self.world = world
        self.font = font
        self.initialized = False

        self.sprites = []

        # Input state
        self.seed_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        # Fade effects
        self.menu_alpha = 0
        self.fading_out = False
        self.fade_alpha = 0

        self.TITLE: Surface = pygame.transform.scale(
            pygame.image.load('assets/title.png').convert_alpha(), (104 * 4.4, 16 * 4.4)
        )

        # Background image scaled by 2x
        self.BACK: Surface = pygame.transform.scale(
            pygame.image.load('assets/back.png').convert(), (384 * 2.5, 163 * 2.5)
        )

        # Initialize surfaces and rectangles
        self.overlay = Surface(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
        self.overlay.fill((0, 0, 0, 255))

        # Create static text elements
        self.texts = []

        # Edition Text
        edition_text = self.font.render(
            "════════════════ Potato Edition ════════════════",
            False, (137, 229, 160), None
        ).convert_alpha()

        edition_rect = edition_text.get_rect(center=(SCREEN_HALF_W, SCREEN_HALF_H - 60))
        self.texts.append((edition_text, edition_rect))

        # Seed text
        seed_text = self.font.render(" Enter World Seed ", False, Color.GREY, (22, 22, 137)).convert()
        seed_rect = seed_text.get_rect(center=(SCREEN_HALF_W, SCREEN_HALF_H + 24))
        self.texts.append((seed_text, seed_rect))

        # Author text
        author_text = self.font.render("Game by TheBigEye", False, Color.GREY, Color.BLACK).convert()
        author_rect = author_text.get_rect(bottomleft=(4, SCREEN_FULL_H))
        self.texts.append((author_text, author_rect))

        # Version text
        version_text = self.font.render("Infdev 0.31", False, Color.GREY, Color.BLACK).convert()
        version_rect = version_text.get_rect(bottomright=(SCREEN_FULL_W - 4, SCREEN_FULL_H))
        self.texts.append((version_text, version_rect))

        # Input box
        self.seed_input_rect = pygame.Rect(SCREEN_HALF_W - 136, SCREEN_HALF_H + 23, 272, 40)


    def cleanup(self) -> None:
        """Clean up resources"""
        if self.initialized:
            pygame.key.stop_text_input()
            pygame.mixer.music.fadeout(1500)
            pygame.mixer.music.unload()
            self.initialized = False


    def update(self) -> None:
        if not self.initialized:
            pygame.mixer.music.load('./assets/sounds/titleTheme.ogg')
            pygame.mixer.music.play(-1, fade_ms=10000)
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(self.seed_input_rect)
            self.initialized = True

        if self.fading_out:
            self.fade_alpha = min(self.fade_alpha + 5, 255)
            if self.fade_alpha >= 255:
                self.cleanup()
                world_seed = self.seed_input if self.seed_input else str(randint(-(2**19937-1), 2**19937-1))
                self.world.initialize(world_seed)
            return

        # Update fade effects
        self.menu_alpha = min(self.menu_alpha + 3, 255)
        if self.menu_alpha < 255:
            self.overlay.set_alpha(255 - self.menu_alpha)
        else:
            self.overlay = None

        # Update cursor blink
        self.cursor_timer = (self.cursor_timer + 1) % 8
        if self.cursor_timer == 0:
            self.cursor_visible = not self.cursor_visible

        # Handle events
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                self.cleanup()
                pygame.quit()
            elif evt.type == pygame.TEXTINPUT and len(self.seed_input) < 32:
                self.seed_input += evt.text
                Sound.play("typingSound")
            elif evt.type == pygame.KEYDOWN:
                if evt.key == pygame.K_RETURN and not self.fading_out:
                    self.fading_out = True
                    Sound.play("confirmSound")
                elif evt.key == pygame.K_BACKSPACE:
                    self.seed_input = self.seed_input[:-1]


    def render(self, screen: Surface) -> None:
        self.sprites.clear()

        self.sprites.append((self.BACK, self.BACK.get_rect(center = (SCREEN_HALF_W, 260))))
        self.sprites.append((self.TITLE, self.TITLE.get_rect(center = (SCREEN_HALF_W, 160))))

        self.sprites.extend(Screen.draw_box(21, 18, 18, 3))
        self.sprites.extend(self.texts)

        # Render input text
        input_text = self.font.render(
            self.seed_input + ("█" if self.cursor_visible else " "),
            False, Color.WHITE, (22, 22, 137)
        ).convert()
        self.sprites.append((input_text, input_text.get_rect(center=self.seed_input_rect.center)))

        # Add overlay if still fading
        if self.overlay:
            self.sprites.append((self.overlay, (0, 0)))

        # Add fade out overlay
        if self.fading_out:
            fade_overlay = Surface(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
            fade_overlay.fill((0, 0, 0, self.fade_alpha))
            self.sprites.append((fade_overlay, (0, 0)))

        # Render all sprites
        screen.fblits(self.sprites)
