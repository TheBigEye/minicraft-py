import pygame

from source.utils.constants import TILE_SIZE

ATLAS: pygame.Surface = pygame.image.load('assets/atlas.png').convert_alpha()


class Sprites:

    @staticmethod
    def get(x: int, y: int, step: int, scale: int) -> pygame.Surface:
        """ Extract and scale a sprite from the atlas """
        return pygame.transform.scale(
            ATLAS.subsurface((x * step, y * step, step, step)), (scale, scale)
        )


    # Basic sprites
    NULL_TILE = [get(0, 31, 16, TILE_SIZE)]
    HIGHLIGHT = get(1, 31, 16, TILE_SIZE)

    # UI elements
    HEART_FULL = get(4, 62, 8, 16)
    HEART_NONE = get(5, 62, 8, 16)
    STAMINA_FULL = get(4, 63, 8, 16)
    STAMINA_NONE = get(5, 63, 8, 16)

    GUI_TOP_BORDER = get(7, 62, 8, 16)
    GUI_BACKGROUND = get(7, 63, 8, 16)
    GUI_TOP_LEFT_CORNER = get(6, 62, 8, 16)
    GUI_LEFT_BORDER = get(6, 63, 8, 16)

    GUI_BOTTOM_LEFT_CORNER = pygame.transform.flip(GUI_TOP_LEFT_CORNER, False, True)
    GUI_TOP_RIGHT_CORNER = pygame.transform.flip(GUI_TOP_LEFT_CORNER, True, False)
    GUI_RIGHT_BORDER = pygame.transform.flip(GUI_LEFT_BORDER, True, False)
    GUI_BOTTOM_RIGHT_CORNER = pygame.transform.flip(GUI_TOP_LEFT_CORNER, True, True)
    GUI_BOTTOM_BORDER = pygame.transform.flip(GUI_TOP_BORDER, False, True)


    WATER_SWIM = [
        get(4, 31, 16, TILE_SIZE),
        get(5, 31, 16, TILE_SIZE),
    ]


    # Base terrain sprites
    GRASS = [
        get(1, 1, 16, TILE_SIZE),  # Base grass

        get(1, 0, 16, TILE_SIZE),  # Top transition
        get(2, 1, 16, TILE_SIZE),  # Left transition
        get(0, 1, 16, TILE_SIZE),  # Right transition
        get(1, 2, 16, TILE_SIZE),  # Bottom transition

        get(0, 0, 16, TILE_SIZE),  # Top-left corner
        get(2, 0, 16, TILE_SIZE),  # Top-right corner
        get(0, 2, 16, TILE_SIZE),  # Bottom-left corner
        get(2, 2, 16, TILE_SIZE),   # Bottom-right corner

        get(0, 3, 16, TILE_SIZE),  # Base grass 2
    ]

    HOLE = [
        get(4, 1, 16, TILE_SIZE),  # Base hole

        get(4, 0, 16, TILE_SIZE),  # Top transition
        get(5, 1, 16, TILE_SIZE),  # Left transition
        get(3, 1, 16, TILE_SIZE),  # Right transition
        get(4, 2, 16, TILE_SIZE),  # Bottom transition

        get(3, 0, 16, TILE_SIZE),  # Top-left corner
        get(5, 0, 16, TILE_SIZE),  # Top-right corner
        get(3, 2, 16, TILE_SIZE),  # Bottom-left corner
        get(5, 2, 16, TILE_SIZE),  # Bottom-right corner
    ]

    SAND = [
        get(13, 1, 16, TILE_SIZE), # Base sand

        get(13, 0, 16, TILE_SIZE), # Top transition
        get(14, 1, 16, TILE_SIZE), # Left transition
        get(12, 1, 16, TILE_SIZE), # Right transition
        get(13, 2, 16, TILE_SIZE), # Bottom transition

        get(12, 0, 16, TILE_SIZE), # Top-left corner
        get(14, 0, 16, TILE_SIZE), # Top-right corner
        get(12, 2, 16, TILE_SIZE), # Bottom-left corner
        get(14, 2, 16, TILE_SIZE), # Bottom-right corner
    ]

    SNOW = [
        get(7, 1, 16, TILE_SIZE), # Base snow

        get(7, 0, 16, TILE_SIZE), # Top transition
        get(8, 1, 16, TILE_SIZE), # Left transition
        get(6, 1, 16, TILE_SIZE), # Right transition
        get(7, 2, 16, TILE_SIZE), # Bottom transition

        get(6, 0, 16, TILE_SIZE), # Top-left corner
        get(8, 0, 16, TILE_SIZE), # Top-right corner
        get(6, 2, 16, TILE_SIZE), # Bottom-left corner
        get(8, 2, 16, TILE_SIZE), # Bottom-right corner

        get(6, 3, 16, TILE_SIZE), # Base snow 2
    ]

    ICE = [
        get(10, 1, 16, TILE_SIZE), # Base ice

        get(10, 0, 16, TILE_SIZE), # Top transition
        get(11, 1, 16, TILE_SIZE), # Left transition
        get(9, 1, 16, TILE_SIZE),  # Right transition
        get(10, 2, 16, TILE_SIZE), # Bottom transition

        get(9, 0, 16, TILE_SIZE),  # Top-left corner
        get(11, 0, 16, TILE_SIZE), # Top-right corner
        get(9, 2, 16, TILE_SIZE),  # Bottom-left corner
        get(11, 2, 16, TILE_SIZE), # Bottom-right corner

        get(10, 3, 16, TILE_SIZE), # Base ice 2
        get(10, 3, 16, TILE_SIZE), # Base ice 3
    ]


    ICEBERG = [
        get(9, 3, 16, TILE_SIZE),
        get(11, 3, 16, TILE_SIZE)
    ]

    CACTUS = [
        get(0, 5, 16, TILE_SIZE)
    ]

    WATER = [
        get(16, 1, 16, TILE_SIZE), # Base water

        get(16, 0, 16, TILE_SIZE), # Top transition
        get(17, 1, 16, TILE_SIZE), # Left transition
        get(15, 1, 16, TILE_SIZE),  # Right transition
        get(16, 2, 16, TILE_SIZE), # Bottom transition

        get(15, 0, 16, TILE_SIZE),  # Top-left corner
        get(17, 0, 16, TILE_SIZE), # Top-right corner
        get(15, 2, 16, TILE_SIZE),  # Bottom-left corner
        get(17, 2, 16, TILE_SIZE), # Bottom-right corner

        get(15, 3, 16, TILE_SIZE), # Base water 2
        get(16, 3, 16, TILE_SIZE), # Base water 3
    ]

    DIRT = [
        get(3, 3, 16, TILE_SIZE),
        get(4, 3, 16, TILE_SIZE)
    ]


    # Tree sprites
    OAK_TREE = [
        get(0, 4, 32, TILE_SIZE * 2),
        get(1, 4, 32, TILE_SIZE * 2)
    ]

    BIRCH_TREE = [
        get(0, 5, 32, TILE_SIZE * 2),
        #get(1, 5, 32, TILE_SIZE * 2)
        get(0, 5, 32, TILE_SIZE * 2),
    ]

    PINE_TREE = [
        get(0, 6, 32, TILE_SIZE * 2),
        get(1, 6, 32, TILE_SIZE * 2)
    ]

    # Player sprites [down, left, right, up]
    PLAYER = [
        [get(0, 16, 16, TILE_SIZE), get(1, 16, 16, TILE_SIZE)],
        [get(0, 18, 16, TILE_SIZE), get(1, 18, 16, TILE_SIZE)],
        [get(0, 17, 16, TILE_SIZE), get(1, 17, 16, TILE_SIZE)],
        [get(0, 15, 16, TILE_SIZE), get(1, 15, 16, TILE_SIZE)],
    ]

    VAMP = [
        [get(3, 16, 16, TILE_SIZE), get(4, 16, 16, TILE_SIZE)],
        [get(3, 18, 16, TILE_SIZE), get(4, 18, 16, TILE_SIZE)],
        [get(3, 17, 16, TILE_SIZE), get(4, 17, 16, TILE_SIZE)],
        [get(3, 15, 16, TILE_SIZE), get(4, 15, 16, TILE_SIZE)],
    ]

    PIG = [
        [get(6, 16, 16, TILE_SIZE), get(7, 16, 16, TILE_SIZE)],
        [get(6, 18, 16, TILE_SIZE), get(7, 18, 16, TILE_SIZE)],
        [get(6, 17, 16, TILE_SIZE), get(7, 17, 16, TILE_SIZE)],
        [get(6, 15, 16, TILE_SIZE), get(7, 15, 16, TILE_SIZE)],
    ]

    SHEEP = [
        [get(9, 16, 16, TILE_SIZE), get(10, 16, 16, TILE_SIZE)],
        [get(9, 18, 16, TILE_SIZE), get(10, 18, 16, TILE_SIZE)],
        [get(9, 17, 16, TILE_SIZE), get(10, 17, 16, TILE_SIZE)],
        [get(9, 15, 16, TILE_SIZE), get(10, 15, 16, TILE_SIZE)],
    ]
