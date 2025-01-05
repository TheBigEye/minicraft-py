import pygame
from pygame import Surface

from source.screen.screen import Color

from source.utils.constants import (
    CHUNK_SIZE, TILE_SIZE,
    RENDER_RANGE_H, RENDER_RANGE_V,
    SCREEN_HALF_W, SCREEN_HALF_H
)

from source.game import Game
from source.utils.region import Region


class Debug:
    # Cache chunk size in pixels
    CHUNK_PIXELS = CHUNK_SIZE * TILE_SIZE
    REGION_PIXELS = CHUNK_PIXELS * Region.REGION_SIZE

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
                color = (Color.DARK_GREY if chunk_pos == current_chunk else
                        Color.RED if not all_neighbors_generated else
                        Color.GREEN)

                # Draw rectangles using integer coordinates
                pygame.draw.rect(screen, color, chunk_rect, 2)
                pygame.draw.rect(screen, color, chunk_rect.inflate(-2, -2), 1)

                # Render chunk coordinates
                coord_text = f"C: {xc},{yc}"
                text_surface = Game.font.render(coord_text, False, Color.WHITE).convert()
                text_rect = text_surface.get_rect()

                # Create background for text
                background = pygame.Surface((text_rect.width + 4, text_rect.height + 2)).convert()
                background.fill(Color.BLACK)

                # Position text in top-left corner with small padding
                screen.blit(background, (xr + 2, yr + 2))
                screen.blit(text_surface, (xr + 4, yr + 2))

                # Add region label under chunk label
                rx_current, ry_current = xc // Region.REGION_SIZE, yc // Region.REGION_SIZE
                region_text = f"R: {rx_current},{ry_current}"
                text_surface = Game.font.render(region_text, False, Color.WHITE).convert()
                text_rect = text_surface.get_rect()

                # Create background for region text
                background = pygame.Surface((text_rect.width + 4, text_rect.height + 2)).convert()
                background.fill(Color.BLACK)

                # Position region text below chunk label
                screen.blit(background, (xr + 2, yr + 20))
                screen.blit(text_surface, (xr + 4, yr + 20))


        # Draw current region boundary only
        current_rx, current_ry = cx // Region.REGION_SIZE, cy // Region.REGION_SIZE

        region_rect = pygame.Rect(
            xo + (current_rx * Debug.REGION_PIXELS) - (cx * Debug.CHUNK_PIXELS),
            yo + (current_ry * Debug.REGION_PIXELS) - (cy * Debug.CHUNK_PIXELS),
            Debug.REGION_PIXELS,
            Debug.REGION_PIXELS
        )

        pygame.draw.rect(screen, Color.RED, region_rect, 4)
        pygame.draw.rect(screen, Color.DARK_RED, region_rect.inflate(-4, -4), 2)
