from pygame import QUIT, display, event, time

from source.core.game import Game
from source.core.player import Player
from source.core.sound import Sound
from source.core.updater import Updater

from source.level.world import World

from source.screen.color import Color
from source.screen.hotbar import Hotbar
from source.screen.shader import Shader
from source.screen.startmenu import StartMenu

from source.utils.constants import GAME_TICKS
from source.utils.saveload import Saveload


def main() -> None:
    Game.initialize()
    Sound.initialize()

    player = Player()
    world = World(player)
    updater = Updater(world, player)

    title = StartMenu(world, Game.font)
    hotbar = Hotbar(player, Game.font)
    shader = Shader()


    # You might be wondering, why complicate things with a complex main loop when
    # Pygame makes it so much simpler and faster? The answer is straightforward
    # and comes down to two reasons:
    #
    # - While a basic Pygame main loop is easy to implement, it tends to consume
    # an excessive and valuable amount of CPU resources. I'm not exaggerating,
    # even when limiting the game to 30 FPS, it's still inefficient
    #
    # - Lastly, I'm accustomed to using the original main loop design from Minicraft
    # on Java, so it's a method I'm familiar and comfortable with

    clock = time.Clock()
    timer = time.get_ticks()
    delta = 0.00

    this_time: int = time.get_ticks()
    last_time: int = time.get_ticks()
    frame_time = 1000 // GAME_TICKS

    running: bool = True
    drawing: bool = False

    while running:
        this_time = time.get_ticks()
        delta += this_time - last_time
        last_time = this_time

        drawing = False

        # GAME LOGIC UPDATE
        while delta >= frame_time:

            for _ in event.get(QUIT):
                running = False

            if world.loaded:
                updater.update()
                hotbar.update()
            else:
                title.update()

            delta -= frame_time
            drawing = True


        # SCREEN UPDATE
        if drawing:
            if Game.debug:
                render_start = time.get_ticks()

            # Clear the screen improve the performance
            Game.buffer.fill(Color.BLACK)

            if world.loaded:
                world.render(Game.buffer)
                hotbar.render(Game.buffer)
            else:
                title.render(Game.buffer)

            shader.render(Game.buffer)

            display.flip()

            if Game.debug:
                render_time = time.get_ticks() - render_start


        clock.tick_busy_loop(GAME_TICKS)


        # DEBUG ...
        if Game.debug and (time.get_ticks() - timer) >= 1000:
            if drawing:
                print(f"> render time: {render_time} ms")

            timer = time.get_ticks()


    # This prevents corrupted save files in case the game is closed
    if world.loaded:
        Saveload.save(updater, world, player)

    Sound.quit()
    Game.quit()


if __name__ == "__main__":
    main()
