from time import time, time_ns

import pygame
from pygame import display, event, QUIT

from source.game import Game
from source.sound import Sound

from source.core.player import Player
from source.level.world import World

from source.screen.hotbar import Hotbar
from source.screen.screen import Color
from source.screen.shader import Shader
from source.screen.startmenu import StartMenu

from source.utils.saveload import Saveload
from source.utils.updater import Updater
from source.utils.constants import GAME_TICKS


def main() -> None:
    Game.initialize()
    Sound.initialize()

    player = Player()
    world = World(player)
    updater = Updater(world, player)

    try:
        Saveload.load(updater, world, player)
    except FileNotFoundError:
        world.loaded = False

    clock = pygame.time.Clock()
    title = StartMenu(world, Game.font)
    hotbar = Hotbar(player, Game.font)
    shader = Shader()

    # You might be wondering, why complicate things with a custom main loop when
    # Pygame makes it so much simpler and faster? The answer is straightforward
    # and comes down to three reasons:
    #
    # - While a basic Pygame main loop is easy to implement, it tends to consume
    # an excessive and valuable amount of CPU resources. I'm not exaggerating,
    # even when limiting the game to 30 FPS, it's still inefficient
    #
    # - This approach provides greater control and precision, allowing for finer
    # adjustments to the game's timing and performance
    #
    # - Lastly, I'm accustomed to using the original main loop from Minicraft in
    # Java, so it's a method I'm familiar and comfortable with

    this_time: int = time_ns()
    last_time: int = this_time
    nano_time: float = 1000000000.0 / GAME_TICKS

    timer = time() * 1000
    delta: float = 0.00

    running: bool = True
    drawing: bool = False

    # Only calculate render time if Game.debug is True
    screen_time: float = 0.00
    last_screen: float = 0.00

    while running:
        this_time = time_ns()
        delta += (this_time - last_time) / nano_time
        last_time = this_time

        drawing = False

        # GAME LOGIC UPDATE
        while delta >= 1:

            for _ in event.get(QUIT):
                running = False

            if world.loaded:
                updater.update()
                hotbar.update()
            else:
                title.update()

            delta -= 1
            drawing = True


        clock.tick(GAME_TICKS)


        # SCREEN UPDATE
        if drawing:
            if Game.debug:
                screen_time = time() * 1000

            Game.buffer.fill(Color.BLACK)

            if world.loaded:
                world.render(Game.buffer)
                hotbar.render(Game.buffer)
            else:
                title.render(Game.buffer)

            shader.render(Game.buffer)

            Game.screen.blit(Game.buffer, (0, 0))
            display.flip()

            if Game.debug:
                last_screen = (time() * 1000) - screen_time

        # DEBUG ...
        if ((time() * 1000) - timer) > 1000:
            if Game.debug:
                print(f"> render time: {last_screen:.2f}ms")
                #print(f"> FPS: {clock.get_fps():.2f}")

            timer += 1000

    # This prevents corrupted save files in case the game is closed
    if world.loaded:
        Saveload.save(updater, world, player)

    Sound.quit()
    Game.quit()


if __name__ == "__main__":
    main()
