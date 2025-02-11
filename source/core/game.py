from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from source.core.debugger import Debugger
from source.core.updater import Updater
from source.screen.color import Color
from source.screen.hotbar import Hotbar
from source.screen.shader import Shader
from source.utils.constants import SCREEN_HALF
from source.utils.saveload import Saveload

if TYPE_CHECKING:
    from source.core.initializer import Initializer
    from source.custom.custom import Custom
    from source.core.sound import Sound
    from source.screen.menu.menu import Menu
    from source.screen.screen import Screen
    from source.screen.sprites import Sprites
    from source.world.world import World


class Game:
    """ Main game class """

    def __init__(self):

        self.VERSION = "Alpha"
        self.ENGINE  = "Toutetsu Engine"
        self.PYGAME  = pygame.version.ver

        self.debug: bool = False
        self.focus: bool = True

        self.sound: Sound = None # Sound manager
        self.screen: Screen = None
        self.sprites: Sprites = None
        self.menu: Menu = None
        self.world: World = None # World manager

        self.updater: Updater = None
        self.hotbar: Hotbar = None
        self.shader: Shader = None

        self.tick_time: int = 0
        self.game_time: int = 0

        self.custom: Custom = None


    def initialize(self, initializer: Initializer) -> None:
        """Initialize game with required dependencies"""
        self.screen = initializer.screen
        self.sprites = initializer.sprites
        self.sound = initializer.sound
        self.world = initializer.world
        self.custom = initializer.custom

        self.debugger = Debugger(self)

        self.updater = Updater(self)
        self.hotbar = Hotbar(self.sprites, self.world.player)
        self.shader = Shader()


    def set_menu(self, menu: Menu) -> None:
        if menu:
            self.menu = menu
            if self.menu:
                self.menu.initialize(self)
        else:
            self.menu = None


    def update(self) -> None:
        self.tick_time += 1

        if not pygame.key.get_focused():
            return

        if self.menu:
            self.menu.update()
            return

        if (self.world.loaded):
            self.updater.update()
            self.hotbar.update()


    def render(self) -> None:
        self.screen.buffer.fill(0)

        if self.world.loaded:
            self.world.render(self.screen)

            if self.debug:
                # Chunks grid
                self.debugger.grid(self.screen)
                self.debugger.info(self.screen)

            self.hotbar.render(self.screen)

        if self.menu:
            self.menu.render(self.screen)

        if not pygame.key.get_focused():
            self.focus_nagger(self.screen)

        # NOTE: render the shader drops FPS!
        # self.shader.render(self.screen)


    def focus_nagger(self, screen: Screen):
        """ A focus nagger :D """

        text = "Click to focus!"

        # Calculate box position (convert pixels to tile units)
        x = (SCREEN_HALF[0] // 16) - 6
        y = (SCREEN_HALF[1] // 16) - 1

        # Create box and initialize sprites list
        sprites = screen.draw_box(x, y, 12, 3)

        # Set color based on update count
        color = Color.GRAY if (self.tick_time / 2) % 2 == 0 else Color.WHITE

        text_position = (SCREEN_HALF[0], SCREEN_HALF[1] - 7)

        # Create shadow text
        shadow = screen.font.render(text, False, Color.BLACK).convert()
        shadow_rect = shadow.get_rect(center = (text_position[0] + 1, text_position[1] + 1))
        sprites.append((shadow, (shadow_rect.x, shadow_rect.y)))

        # Create main text
        message = screen.font.render(text, False, color).convert()
        message_rect = message.get_rect(center = text_position)
        sprites.append((message, (message_rect.x, message_rect.y)))

        screen.buffer.fblits(sprites)


    def quit(self) -> None:
        """ Quit the game """

        # This prevents corrupted save files in case the game is closed
        if self.world.loaded:
            Saveload.save(self.updater)

        self.sound.quit()

        pygame.display.quit()
        pygame.font.quit()
        pygame.quit()
