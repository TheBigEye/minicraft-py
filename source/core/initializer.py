from __future__ import annotations

import pygame
from pygame import QUIT, display, event, time


from source.core.game import Game
from source.core.player import Player
from source.core.sound import Sound
from source.screen.menu.titlemenu import TitleMenu
from source.screen.screen import Screen
from source.screen.sprites import Sprites
from source.world.tiles import Tiles
from source.world.world import World

from source.utils.constants import GAME_TICKS

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

        # Core systems first
        self.screen = Screen()
        self.sprites = Sprites()
        self.sound = Sound()

        # Initialize core resources
        self.screen.initialize()
        self.sprites.initialize()
        self.sound.initialize()

        # Game state objects
        self.game = Game()
        tiles = Tiles(self.sprites)
        player = Player(self.sprites, self.game)
        self.world = World(self.sprites, tiles, player)

        # Initialize game
        self.game.initialize(
            # We need their dependencies :)
            screen=self.screen,
            sprites=self.sprites,
            sound=self.sound,
            world=self.world
        )

        # Set initial game state
        self.game.display(TitleMenu())
        pygame.event.set_blocked(None)
        pygame.event.set_allowed([QUIT, pygame.KEYDOWN, pygame.TEXTINPUT])


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
