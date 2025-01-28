from pygame import QUIT, display, event, time

from source.core.game import Game
from source.core.player import Player
from source.core.sound import Sound
from source.screen.menu.titlemenu import TitleMenu
from source.screen.screen import Screen
from source.screen.sprites import Sprites
from source.utils.constants import GAME_TICKS
from source.world.tiles import Tiles
from source.world.world import World


def main() -> None:

    screen = Screen()
    sprites = Sprites()

    game = Game()
    sound = Sound()

    tiles = Tiles(sprites)
    player = Player(sprites, game)
    world = World(sprites, tiles, player)

    game.initialize(
        sound,
        screen,
        sprites,
        world
    )

    game.display(TitleMenu())

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

            game.update()

            delta -= frame_time
            drawing = True


        # SCREEN UPDATE
        if drawing:
            if game.debug:
                render_start = time.get_ticks()

            game.render()

            display.flip()

            if game.debug:
                render_time = time.get_ticks() - render_start


        clock.tick(GAME_TICKS)


        # DEBUG ...
        if game.debug and (time.get_ticks() - timer) >= 1000:
            if drawing:
                print(f"> render time: {render_time} ms")

            timer = time.get_ticks()


    game.quit()


if __name__ == "__main__":
    main()
