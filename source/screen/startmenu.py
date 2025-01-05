from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

import pygame
from pygame import Font, Surface

from source.screen.screen import Color
from source.screen.sprites import TITLE
from source.sound import Sound

from source.utils.constants import (
    SCREEN_SIZE_T, SCREEN_HALF_W,
    SCREEN_HALF_H, SCREEN_FULL_W,
    SCREEN_FULL_H
)

if TYPE_CHECKING:
    from source.core.world import World

class StartMenu:
    def __init__(self, world: World, font: Font) -> None:
        self.world = world
        self.font = font
        self.initialized = False

        # Input state
        self.seed_input = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        # Fade effects
        self.menu_alpha = 0
        self.title_alpha = 0
        self.color_increment = 3

        # Pre-render static elements
        self._init_surfaces()

    def _init_surfaces(self) -> None:
        """Initialize static surfaces and rectangles"""
        # Create overlay surface
        self.overlay = pygame.Surface(SCREEN_SIZE_T, pygame.SRCALPHA, 32).convert_alpha()
        self.overlay.fill((0, 0, 0, 255))

        # Create static text elements
        self.texts = []

        # Seed text
        seed_text = self.font.render("Enter World Seed:", False, Color.CYAN, Color.BLACK).convert()
        seed_rect = seed_text.get_rect(center=(SCREEN_HALF_W, SCREEN_HALF_H + 32))
        self.texts.append((seed_text, seed_rect))

        # Author text
        author_text = self.font.render("Game by TheBigEye", False, Color.CYAN, Color.BLACK).convert()
        author_rect = author_text.get_rect(bottomleft=(4, SCREEN_FULL_H))
        self.texts.append((author_text, author_rect))

        # Version text
        version_text = self.font.render("Infdev 0.31", False, Color.CYAN, Color.BLACK).convert()
        version_rect = version_text.get_rect(bottomright=(SCREEN_FULL_W - 4, SCREEN_FULL_H))
        self.texts.append((version_text, version_rect))

        # Input box
        self.seed_input_rect = pygame.Rect(SCREEN_HALF_W - 136, SCREEN_HALF_H + 48, 272, 40)

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.initialized:
            pygame.key.stop_text_input()
            pygame.mixer.music.fadeout(2000)
            pygame.mixer.music.unload()
            self.initialized = False

    def _handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events"""
        if event.type == pygame.TEXTINPUT and len(self.seed_input) < 32:
            self.seed_input += event.text
            Sound.play("typingSound")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_game()
            elif event.key == pygame.K_BACKSPACE:
                self.seed_input = self.seed_input[:-1]

    def _start_game(self) -> None:
        """Start the game with the current seed"""
        self.cleanup()
        world_seed = self.seed_input if self.seed_input else str(randint(-(2**19937-1), 2**19937-1))
        Sound.play("confirmSound")
        self.world.initialize(world_seed)

    def update(self) -> None:
        if not self.initialized:
            pygame.mixer.music.load('./assets/sounds/titleTheme.ogg')
            pygame.mixer.music.play(-1, fade_ms=12000)
            pygame.key.start_text_input()
            pygame.key.set_text_input_rect(self.seed_input_rect)
            self.initialized = True

        # Update fade effects
        self.menu_alpha = min(self.menu_alpha + 3, 255)
        if self.menu_alpha < 255:
            self.overlay.set_alpha(255 - self.menu_alpha)
        else:
            self.overlay = None

        # Update title animation
        self.title_alpha = min(max(self.title_alpha + self.color_increment, 128), 255)
        if self.title_alpha >= 250 or self.title_alpha <= 128:
            self.color_increment = -self.color_increment

        # Update cursor blink
        self.cursor_timer = (self.cursor_timer + 1) % 8
        if self.cursor_timer == 0:
            self.cursor_visible = not self.cursor_visible

        # Handle events
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                self.cleanup()
                pygame.quit()
            else:
                self._handle_input(evt)

        TITLE.set_alpha(self.title_alpha)

    def render(self, screen: Surface) -> None:
        sprites = []

        sprites.append((TITLE, TITLE.get_rect(center = (SCREEN_HALF_W, 160))))
        sprites.extend(self.texts)

        # Render input text
        input_text = self.font.render(
            self.seed_input + ("█" if self.cursor_visible else " "),
            False, Color.GREY, Color.BLACK
        ).convert()
        sprites.append((input_text, input_text.get_rect(center=self.seed_input_rect.center)))

        # Draw input box
        pygame.draw.rect(screen, Color.CYAN, self.seed_input_rect, 1)

        # Add overlay if still fading
        if self.overlay:
            sprites.append((self.overlay, (0, 0)))

        # Render all sprites
        screen.fblits(sprites)
