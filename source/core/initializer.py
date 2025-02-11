from __future__ import annotations

import pygame
from pygame import KEYDOWN, QUIT, TEXTINPUT, display, event, time

from source.core.game import Game
from source.core.player import Player
from source.core.sound import Sound
from source.custom.custom import Custom
from source.screen.menu.titlemenu import TitleMenu
from source.screen.screen import Screen
from source.screen.sprites import Sprites
from source.utils.constants import GAME_TICKS
from source.world.tiles import Tiles
from source.world.world import World


class Initializer:

    def __init__(self) -> None:
        self.screen: Screen = None
        self.sprites: Sprites = None
        self.sound: Sound = None
        self.game: Game = None
        self.world: World = None
        self.running: bool = False


    def initialize(self) -> None:
        """ Initialize all game systems """

        # We make the game object
        self.game = Game()

        # Core systems first
        self.screen = Screen()
        self.sprites = Sprites()
        self.sound = Sound()

        # Initialize core resources
        self.sprites.initialize()
        self.sound.initialize()

        # Initialize the screen
        self.screen.initialize(self.sprites)

        # Setup game objects
        tiles = Tiles(self.sprites)
        player = Player(self.sprites, self.game)
        self.world = World(self.game, self.sprites, tiles, player)

        # Mods subsystem
        self.custom = Custom(self.sprites, tiles)

        # Initialize game
        self.game.initialize(self)

        # Set initial game state
        self.game.set_menu(TitleMenu())

        pygame.event.set_blocked(None)
        pygame.event.set_allowed([QUIT, KEYDOWN, TEXTINPUT])


    def run(self) -> None:
        """ Main game loop """

        self.running = True

        clock = time.Clock()
        timer = time.get_ticks()
        delta = 0.00

        this_time: int = time.get_ticks()
        last_time: int = time.get_ticks()
        frame_time = 1000 // GAME_TICKS

        while self.running:
            this_time = time.get_ticks()
            delta += this_time - last_time
            last_time = this_time

            drawing = False

            # Game logic update
            while delta >= frame_time:
                for _ in event.get(QUIT):
                    self.running = False

                self.game.update()
                delta -= frame_time
                drawing = True

            # Screen update
            if drawing:
                render_start = time.get_ticks() if self.game.debug else 0

                self.game.render()
                display.flip()

                if self.game.debug:
                    render_time = time.get_ticks() - render_start

            clock.tick(GAME_TICKS)

            # Debug output
            if self.game.debug and (time.get_ticks() - timer) >= 1000:
                if drawing:
                    print(f"> render time: {render_time} ms")
                timer = time.get_ticks()

        self.game.quit()
