from __future__ import annotations

from typing import TYPE_CHECKING

from pygame import Rect, Surface
from pygame.draw import rect

from source.core.game import Game
from source.screen.color import Color

from source.utils.region import Region

from source.utils.constants import (
    CHUNK_SIZE, RENDER_RANGE_H, RENDER_RANGE_V,
    SCREEN_HALF_H, SCREEN_HALF_W, TILE_SIZE,
    DIRECTIONS
)

if TYPE_CHECKING:
    from source.core.player import Player
    from source.screen.screen import Screen

class Debug:
    # Cache chunk size in pixels
    CHUNK_PIXELS = CHUNK_SIZE * TILE_SIZE
    REGION_PIXELS = CHUNK_PIXELS * Region.REGION_SIZE

    @staticmethod
    def grid(screen: Screen, chunks: dict, player: Player) -> None:

        cx = player.cx
        cy = player.cy

        # Offset for chunks grid
        xo = int(SCREEN_HALF_W - ((player.position.x - cx * CHUNK_SIZE) * TILE_SIZE))
        yo = int(SCREEN_HALF_H - ((player.position.y - cy * CHUNK_SIZE) * TILE_SIZE))

        # Create rectangle for the chunk
        chunk_rect = Rect(0, 0, Debug.CHUNK_PIXELS, Debug.CHUNK_PIXELS)

        current_chunk_color = Color.GREEN
        missing_chunk_color = Color.RED
        normal_chunk_color = Color.BLACK

        x_start = -(RENDER_RANGE_H + 1)
        x_end = RENDER_RANGE_H + 2
        y_start = -RENDER_RANGE_V
        y_end = RENDER_RANGE_V + 1

        for x in range(x_start, x_end):
            xr = int(x * Debug.CHUNK_PIXELS + xo)
            xc = cx + x

            for y in range(y_start, y_end):
                yr = int(y * Debug.CHUNK_PIXELS + yo)
                yc = cy + y

                # Check if current chunk
                current_chunk = xc == cx and yc == cy

                # Only check neighbors if not current chunk
                if not current_chunk:
                    # Also we check if neighbors has been generated
                    neighbors_generated = all(
                        (xc + dx, yc + dy) in chunks
                        for dx, dy in DIRECTIONS
                    )
                else:
                    neighbors_generated = True

                # Update rectangle position
                chunk_rect.x = xr
                chunk_rect.y = yr

                # Determine color based on chunk status
                color = (current_chunk_color if current_chunk else
                        missing_chunk_color if not neighbors_generated else
                        normal_chunk_color)

                # Draw rectangles
                rect(screen.buffer, color, chunk_rect, 2)
                chunk_rect.inflate_ip(-2, -2)
                rect(screen.buffer, color, chunk_rect, 1)
                chunk_rect.inflate_ip(2, 2)  # Restore original size

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
            xo + (rx * Debug.REGION_PIXELS) - (cx * Debug.CHUNK_PIXELS),
            yo + (ry * Debug.REGION_PIXELS) - (cy * Debug.CHUNK_PIXELS),
            Debug.REGION_PIXELS,
            Debug.REGION_PIXELS
        )

        rect(screen.buffer, Color.RED, region_rect, 4)
        region_rect.inflate_ip(-4, -4)
        rect(screen.buffer, Color.DARK_RED, region_rect, 2)
