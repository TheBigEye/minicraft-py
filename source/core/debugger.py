from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Rect
from pygame.draw import rect

from source.screen.color import Color
from source.utils.region import Region

from source.utils.constants import (
    TILE_SIZE, CHUNK_SIZE, RENDER_SIZE,
    SCREEN_HALF, DIRECTIONS
)

if TYPE_CHECKING:
    from source.core.game import Game
    from source.core.player import Player
    from source.screen.screen import Screen
    from source.world.world import World


class Debugger:

    def __init__(self, game: Game):

        self.game: Game = game
        self.world: World = self.game.world
        self.player: Player = self.world.player

        # Cache chunk size in pixels
        self.CHUNK_PIXELS = CHUNK_SIZE * TILE_SIZE
        self.REGION_PIXELS = self.CHUNK_PIXELS * Region.REGION_SIZE

        # Grid render distance
        self.RENDER_WIDTH = range(-(RENDER_SIZE[0] + 1), RENDER_SIZE[0] + 2)
        self.RENDER_HEIGHT = range(-RENDER_SIZE[1], RENDER_SIZE[1] + 1)

        self.shadow_offsets = {
            (-1, -1), ( 1,  1),
            ( 0, -1), ( 0,  1),
            (-1,  1), ( 1, -1),
            (-1,  0), ( 1,  0),
        }

        self.chunk_rect = Rect(0, 0, self.CHUNK_PIXELS, self.CHUNK_PIXELS)


    def info(self, screen: Screen) -> None:

        self.custom = self.game.custom.enabled

        text = [
            f"> Minicraft Potato Edition ({self.game.VERSION})",
            f"> {self.game.ENGINE} (pygame-ce {self.game.PYGAME})",
            "",
            f">>> Modded game: {self.custom} <<<",
            "",

            # Player
            f"X: {self.player.position.x} ({self.player.cx})",
            f"Y: {self.player.position.y} ({self.player.cy})",
            f"F: ({self.player.facing.x:.2f}, {self.player.facing.y:.2f})",
            "",

            # World
            f"Chunks: {len(self.world.chunks)}",
            f"Ticks: {self.world.ticks}",
            f"Light: {self.world.daylight()}",
            f"Seed: {self.world.seed}",
        ]

        for i, msg in enumerate(text):
            y = i * 16

            # Render shadow
            shadow_surface = screen.font.render(msg, False, Color.BLACK).convert()
            for xo, yo in self.shadow_offsets:
                screen.buffer.blit(shadow_surface, (4 + xo, y + yo))

            # Render text
            text_surface = screen.font.render(msg, False, Color.WHITE).convert()
            screen.buffer.blit(text_surface, (4, y))


    def grid(self, screen: Screen) -> None:

        cx = self.player.cx
        cy = self.player.cy

        # Offset for chunks grid
        xo = int(SCREEN_HALF[0] - ((self.player.position.x - cx * CHUNK_SIZE) * TILE_SIZE))
        yo = int(SCREEN_HALF[1]- ((self.player.position.y - cy * CHUNK_SIZE) * TILE_SIZE))

        current_chunk_color = Color.YELLOW
        missing_chunk_color = Color.RED
        normal_chunk_color = Color.BROWN

        for x in self.RENDER_WIDTH:
            xr = int(x * self.CHUNK_PIXELS + xo)
            xc = cx + x

            for y in self.RENDER_HEIGHT:
                yr = int(y * self.CHUNK_PIXELS + yo)
                yc = cy + y

                # Check if current chunk
                current_chunk = xc == cx and yc == cy

                # Only check neighbors if not current chunk
                if not current_chunk:
                    # Also we check if neighbors has been generated
                    neighbors_generated = all(
                        (xc + dx, yc + dy) in self.world.chunks
                        for dx, dy in DIRECTIONS
                    )
                else:
                    neighbors_generated = True

                # Update rectangle position
                self.chunk_rect.x = xr
                self.chunk_rect.y = yr

                # Determine color based on chunk status
                color = (current_chunk_color if current_chunk else
                        missing_chunk_color if not neighbors_generated else
                        normal_chunk_color)

                # Draw rectangles
                rect(screen.buffer, color, self.chunk_rect, 2)
                self.chunk_rect.inflate_ip(-2, -2)
                rect(screen.buffer, Color.BLACK, self.chunk_rect, 1)
                self.chunk_rect.inflate_ip(2, 2) # Restore original size

                # Render chunk coordinates
                text_surface = screen.font.render(
                    f"C: {xc},{yc}",
                    False,
                    Color.WHITE,
                    Color.BLACK
                ).convert()
                screen.buffer.blit(text_surface, (xr + 2, yr + 2))

                # And region coordinates
                text_surface = screen.font.render(
                    f"R: {xc // Region.REGION_SIZE},{yc // Region.REGION_SIZE}",
                    False,
                    Color.WHITE,
                    Color.BLACK
                ).convert()
                screen.buffer.blit(text_surface, (xr + 2, yr + 18))

        # Draw current region boundary
        rx, ry = cx // Region.REGION_SIZE, cy // Region.REGION_SIZE
        region_rect = Rect(
            xo + (rx * self.REGION_PIXELS) - (cx * self.CHUNK_PIXELS),
            yo + (ry * self.REGION_PIXELS) - (cy * self.CHUNK_PIXELS),
            self.REGION_PIXELS,
            self.REGION_PIXELS
        )

        rect(screen.buffer, Color.RED, region_rect, 4)
        region_rect.inflate_ip(-4, -4)
        rect(screen.buffer, Color.DARK_RED, region_rect, 2)
