import pygame
from pygame import Surface

from source.screen.screen import Color
from source.utils.constants import *
from source.game import Game  # Add this import


class Debug:
    # Cache chunk size in pixels
    CHUNK_PIXELS = CHUNK_SIZE * TILE_SIZE

    @staticmethod
    def render(screen: Surface, chunks: dict, px: float, py: float, cx: int, cy: int) -> None:
        # Use exact player position for offset calculation to prevent jittering
        player = pygame.Vector2(px, py)
        chunk_pos = pygame.Vector2(cx * CHUNK_SIZE, cy * CHUNK_SIZE)
        offset = (player - chunk_pos) * TILE_SIZE

        # Calculate the offset to center the screen
        xo = int(SCREEN_HALF_W - offset.x)
        yo = int(SCREEN_HALF_H - offset.y)

        # Define the current chunk as a reference
        current_chunk = (cx, cy)

        # Pre-calculate ranges
        x_range = range(-(RENDER_RANGE_H + 1), RENDER_RANGE_H + 2)
        y_range = range(-RENDER_RANGE_V, RENDER_RANGE_V + 1)

        for x in x_range:
            xr = int(x * Debug.CHUNK_PIXELS + xo)
            xc = cx + x

            for y in y_range:
                yr = int(y * Debug.CHUNK_PIXELS + yo)
                yc = cy + y
                chunk_pos = (xc, yc)

                # Only check neighbors if not current chunk
                if chunk_pos != current_chunk:
                    neighbors = (
                        (xc - 1, yc),
                        (xc + 1, yc),
                        (xc, yc - 1),
                        (xc, yc + 1)
                    )
                    all_neighbors_generated = all(n in chunks for n in neighbors)
                else:
                    all_neighbors_generated = True

                # Create rectangle with integer coordinates
                chunk_rect = pygame.Rect(xr, yr, Debug.CHUNK_PIXELS, Debug.CHUNK_PIXELS)

                # Determine color based on chunk status
                color = (Color.MAGENTA if chunk_pos == current_chunk else
                        Color.RED if not all_neighbors_generated else
                        Color.GREEN)

                # Draw rectangles using integer coordinates
                pygame.draw.rect(screen, color, chunk_rect, 2)
                pygame.draw.rect(screen, Color.BLACK, chunk_rect.inflate(-2, -2), 1)

                # Render chunk coordinates
                coord_text = f"{xc},{yc}"
                text_surface = Game.font.render(coord_text, False, Color.WHITE)
                text_rect = text_surface.get_rect()

                # Create background for text
                background = pygame.Surface((text_rect.width + 4, text_rect.height + 2))
                background.fill(Color.BLACK)

                # Position text in top-left corner with small padding
                screen.blit(background, (xr + 2, yr + 2))
                screen.blit(text_surface, (xr + 4, yr + 2))
