
from time import time, time_ns

import pygame

from source.core.mob import mobs
from source.core.player import Player
from source.core.tile import tiles
from source.core.world import World
from source.game import Game
from source.screen.hotbar import Hotbar
from source.screen.screen import Color
from source.screen.shader import Shader
from source.screen.startmenu import StartMenu
from source.sound import Sound
from source.utils.constants import *
from source.utils.saveload import Saveload
from source.utils.updater import Updater


def main() -> None:
    Game.initialize(tiles, mobs)
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

    this_time = time_ns()
    last_time = this_time
    nano_time = 1000000000.0 / GAME_TICKS

    timer = time() * 1000
    delta = 0
    #ticks = 0

    running = True
    drawing = False

    screen_time = time() * 1000

    while running:
        this_time = time_ns()
        delta += (this_time - last_time) / nano_time
        last_time = this_time

        drawing = False

        # GAME LOGIC UPDATE
        while delta >= 1:
            #ticks += 1

            for _ in pygame.event.get(pygame.QUIT):
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
            screen_time = time() * 1000

            Game.buffer.fill(Color.BLACK)

            if world.loaded:
                world.render(Game.buffer)
                hotbar.render(Game.buffer)
                shader.render(Game.buffer)
            else:
                title.render(Game.buffer)

            #shader.render(Game.buffer)

            Game.screen.blit(Game.buffer, (0, 0))

            pygame.display.flip()


        screen_time = (time() * 1000) - screen_time

        # DEBUG ...

        if ((time() * 1000) - timer) > 1000:
            print(
            #    f"> {clock.get_fps():.2f} FPS "
            #    f"/ {ticks} TPS "
            #    f"({world.ticks} daytime) "
            #    f"({world.daylight()} daylight)"
                f"> render time: {screen_time:.2f}ms"
            )

            timer += 1000
            #ticks = 0

    # This prevents corrupted save files in case the game is closed
    if world.loaded:
        Saveload.save(updater, world, player)

    Sound.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
