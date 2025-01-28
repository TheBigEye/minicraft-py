from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from source.core.updater import Updater
from source.screen.hotbar import Hotbar
from source.screen.shader import Shader
from source.utils.saveload import Saveload

if TYPE_CHECKING:
    from source.core.sound import Sound
    from source.screen.menu.menu import Menu
    from source.screen.screen import Screen
    from source.world.tiles import Tiles
    from source.screen.sprites import Sprites
    from source.world.world import World


class Game:
    """ Main game class """

    def __init__(self):
        self.debug: bool = True
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



    def initialize(self, sound: Sound, screen: Screen, sprites: Sprites, world: World) -> None:
        """ Initialize game resources """

        self.sound = sound
        self.screen = screen
        self.sprites = sprites
        self.world = world

        self.sound.initialize()
        self.screen.initialize()
        self.sprites.initialize()

        pygame.event.set_blocked(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.TEXTINPUT])

        self.updater = Updater(self)
        self.hotbar = Hotbar(self.sprites, self.world.player)

        self.shader = Shader()


    def display(self, menu: Menu) -> None:
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

        if self.menu:
            self.menu.render(self.screen)

        if self.world.loaded:
            self.world.render(self.screen)
            self.hotbar.render(self.screen)

        # NOTE: for some reason, render the shader drops FPS!
        self.shader.render(self.screen)


    def quit(self) -> None:
        """ Quit the game """

        # This prevents corrupted save files in case the game is closed
        if self.world.loaded:
            Saveload.save(self.updater)

        self.sound.quit()

        pygame.display.quit()
        pygame.font.quit()
        pygame.quit()
