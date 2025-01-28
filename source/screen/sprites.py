import pygame

from source.utils.constants import TILE_SIZE

class Sprites:

    def __init__(self):
        self.atlas = pygame.image.load('assets/atlas.png').convert_alpha()


    def get(self, x: int, y: int, step: int, scale: int) -> pygame.Surface:
        """ Extract and scale a sprite from the atlas """
        return pygame.transform.scale(
            self.atlas.subsurface((x * step, y * step, step, step)), (scale, scale)
        )

    def initialize(self) -> None:
        """ Initialize all sprites """

        self.NULL = [self.get(0, 31, 16, TILE_SIZE)]
        self.GREEN_EYE = self.get(0, 29, 16, TILE_SIZE)
        self.A_POTATOE = self.get(1, 29, 16, TILE_SIZE)
        self.HIGHLIGHT = self.get(1, 31, 16, TILE_SIZE)

        # UI elements
        self.HEART_FULL = self.get(4, 62, 8, 16)
        self.HEART_NONE = self.get(5, 62, 8, 16)
        self.STAMINA_FULL = self.get(4, 63, 8, 16)
        self.STAMINA_NONE = self.get(5, 63, 8, 16)

        self.GUI_TOP_BORDER = self.get(7, 62, 8, 16)
        self.GUI_BACKGROUND = self.get(7, 63, 8, 16)
        self.GUI_TOP_LEFT_CORNER = self.get(6, 62, 8, 16)
        self.GUI_LEFT_BORDER = self.get(6, 63, 8, 16)

        self.GUI_BOTTOM_LEFT_CORNER = pygame.transform.flip(self.GUI_TOP_LEFT_CORNER, False, True)
        self.GUI_TOP_RIGHT_CORNER = pygame.transform.flip(self.GUI_TOP_LEFT_CORNER, True, False)
        self.GUI_RIGHT_BORDER = pygame.transform.flip(self.GUI_LEFT_BORDER, True, False)
        self.GUI_BOTTOM_RIGHT_CORNER = pygame.transform.flip(self.GUI_TOP_LEFT_CORNER, True, True)
        self.GUI_BOTTOM_BORDER = pygame.transform.flip(self.GUI_TOP_BORDER, False, True)

        self.SMASH_PARTICLE = self.get(6, 31, 16, TILE_SIZE)


        self.WATER_SWIM = [
            self.get(4, 31, 16, TILE_SIZE),
            self.get(5, 31, 16, TILE_SIZE),
        ]


        # Base terrain sprites
        self.GRASS = [
            self.get(1, 1, 16, TILE_SIZE),  # Base grass

            self.get(1, 0, 16, TILE_SIZE),  # Top transition
            self.get(2, 1, 16, TILE_SIZE),  # Left transition
            self.get(0, 1, 16, TILE_SIZE),  # Right transition
            self.get(1, 2, 16, TILE_SIZE),  # Bottom transition

            self.get(0, 0, 16, TILE_SIZE),  # Top-left corner
            self.get(2, 0, 16, TILE_SIZE),  # Top-right corner
            self.get(0, 2, 16, TILE_SIZE),  # Bottom-left corner
            self.get(2, 2, 16, TILE_SIZE),   # Bottom-right corner

            self.get(1, 3, 16, TILE_SIZE),  # Base grass 2
        ]

        self.FLOWERS = [
            self.get(0, 3, 16, TILE_SIZE)
        ]

        self.HOLE = [
            self.get(4, 1, 16, TILE_SIZE),  # Base hole

            self.get(4, 0, 16, TILE_SIZE),  # Top transition
            self.get(5, 1, 16, TILE_SIZE),  # Left transition
            self.get(3, 1, 16, TILE_SIZE),  # Right transition
            self.get(4, 2, 16, TILE_SIZE),  # Bottom transition

            self.get(3, 0, 16, TILE_SIZE),  # Top-left corner
            self.get(5, 0, 16, TILE_SIZE),  # Top-right corner
            self.get(3, 2, 16, TILE_SIZE),  # Bottom-left corner
            self.get(5, 2, 16, TILE_SIZE),  # Bottom-right corner
        ]

        self.SAND = [
            self.get(13, 1, 16, TILE_SIZE), # Base sand

            self.get(13, 0, 16, TILE_SIZE), # Top transition
            self.get(14, 1, 16, TILE_SIZE), # Left transition
            self.get(12, 1, 16, TILE_SIZE), # Right transition
            self.get(13, 2, 16, TILE_SIZE), # Bottom transition

            self.get(12, 0, 16, TILE_SIZE), # Top-left corner
            self.get(14, 0, 16, TILE_SIZE), # Top-right corner
            self.get(12, 2, 16, TILE_SIZE), # Bottom-left corner
            self.get(14, 2, 16, TILE_SIZE), # Bottom-right corner
        ]

        self.SNOW = [
            self.get(7, 1, 16, TILE_SIZE), # Base snow

            self.get(7, 0, 16, TILE_SIZE), # Top transition
            self.get(8, 1, 16, TILE_SIZE), # Left transition
            self.get(6, 1, 16, TILE_SIZE), # Right transition
            self.get(7, 2, 16, TILE_SIZE), # Bottom transition

            self.get(6, 0, 16, TILE_SIZE), # Top-left corner
            self.get(8, 0, 16, TILE_SIZE), # Top-right corner
            self.get(6, 2, 16, TILE_SIZE), # Bottom-left corner
            self.get(8, 2, 16, TILE_SIZE), # Bottom-right corner

            self.get(6, 3, 16, TILE_SIZE), # Base snow 2
        ]

        self.ICE = [
            self.get(10, 1, 16, TILE_SIZE), # Base ice

            self.get(10, 0, 16, TILE_SIZE), # Top transition
            self.get(11, 1, 16, TILE_SIZE), # Left transition
            self.get(9, 1, 16, TILE_SIZE),  # Right transition
            self.get(10, 2, 16, TILE_SIZE), # Bottom transition

            self.get(9, 0, 16, TILE_SIZE),  # Top-left corner
            self.get(11, 0, 16, TILE_SIZE), # Top-right corner
            self.get(9, 2, 16, TILE_SIZE),  # Bottom-left corner
            self.get(11, 2, 16, TILE_SIZE), # Bottom-right corner

            self.get(10, 3, 16, TILE_SIZE), # Base ice 2
            self.get(10, 3, 16, TILE_SIZE), # Base ice 3
        ]


        self.ICEBERG = [
            self.get(9, 3, 16, TILE_SIZE),
            self.get(11, 3, 16, TILE_SIZE)
        ]

        self.CACTUS = [
            self.get(12, 3, 16, TILE_SIZE)
        ]

        self.WATER = [
            self.get(16, 1, 16, TILE_SIZE), # Base water

            self.get(16, 0, 16, TILE_SIZE), # Top transition
            self.get(17, 1, 16, TILE_SIZE), # Left transition
            self.get(15, 1, 16, TILE_SIZE),  # Right transition
            self.get(16, 2, 16, TILE_SIZE), # Bottom transition

            self.get(15, 0, 16, TILE_SIZE),  # Top-left corner
            self.get(17, 0, 16, TILE_SIZE), # Top-right corner
            self.get(15, 2, 16, TILE_SIZE),  # Bottom-left corner
            self.get(17, 2, 16, TILE_SIZE), # Bottom-right corner

            self.get(15, 3, 16, TILE_SIZE), # Base water 2
            self.get(16, 3, 16, TILE_SIZE), # Base water 3
        ]

        self.STONE = [
            self.get(19, 1, 16, TILE_SIZE), # Base water

            self.get(19, 0, 16, TILE_SIZE), # Top transition
            self.get(20, 1, 16, TILE_SIZE), # Left transition
            self.get(18, 1, 16, TILE_SIZE),  # Right transition
            self.get(19, 2, 16, TILE_SIZE), # Bottom transition

            self.get(18, 0, 16, TILE_SIZE),  # Top-left corner
            self.get(20, 0, 16, TILE_SIZE), # Top-right corner
            self.get(18, 2, 16, TILE_SIZE),  # Bottom-left corner
            self.get(20, 2, 16, TILE_SIZE), # Bottom-right corner
        ]

        self.DIRT = [
            self.get(3, 3, 16, TILE_SIZE),
            self.get(4, 3, 16, TILE_SIZE)
        ]


        # Tree sprites
        self.OAK_TREE = [
            self.get(0, 4, 32, TILE_SIZE * 2),
            self.get(1, 4, 32, TILE_SIZE * 2)
        ]

        self.BIRCH_TREE = [
            self.get(0, 5, 32, TILE_SIZE * 2),
            #self.get(1, 5, 32, TILE_SIZE * 2)
            self.get(0, 5, 32, TILE_SIZE * 2),
        ]

        self.PINE_TREE = [
            self.get(0, 6, 32, TILE_SIZE * 2),
            self.get(1, 6, 32, TILE_SIZE * 2)
        ]

        # Player sprites [down, left, right, up]
        self.PLAYER = [
            [self.get(0, 16, 16, TILE_SIZE), self.get(1, 16, 16, TILE_SIZE)],
            [self.get(0, 18, 16, TILE_SIZE), self.get(1, 18, 16, TILE_SIZE)],
            [self.get(0, 17, 16, TILE_SIZE), self.get(1, 17, 16, TILE_SIZE)],
            [self.get(0, 15, 16, TILE_SIZE), self.get(1, 15, 16, TILE_SIZE)],
        ]

        self.WORKBENCH = self.get(0, 25, 16, TILE_SIZE)
        self.ANVIL = self.get(1, 25, 16, TILE_SIZE)
        self.ENCHANTER = self.get(2, 25, 16, TILE_SIZE)
        self.OVEN = self.get(3, 25, 16, TILE_SIZE)
        self.FURNACE = self.get(4, 25, 16, TILE_SIZE)
        self.CHEST = self.get(5, 25, 16, TILE_SIZE)

        self.VAMP = [
            [self.get(3, 16, 16, TILE_SIZE), self.get(4, 16, 16, TILE_SIZE)],
            [self.get(3, 18, 16, TILE_SIZE), self.get(4, 18, 16, TILE_SIZE)],
            [self.get(3, 17, 16, TILE_SIZE), self.get(4, 17, 16, TILE_SIZE)],
            [self.get(3, 15, 16, TILE_SIZE), self.get(4, 15, 16, TILE_SIZE)],
        ]

        self.ZOMBIE = [
            [self.get(3, 21, 16, TILE_SIZE), self.get(4, 21, 16, TILE_SIZE)],
            [self.get(3, 23, 16, TILE_SIZE), self.get(4, 23, 16, TILE_SIZE)],
            [self.get(3, 22, 16, TILE_SIZE), self.get(4, 22, 16, TILE_SIZE)],
            [self.get(3, 20, 16, TILE_SIZE), self.get(4, 20, 16, TILE_SIZE)],
        ]


        self.PIG = [
            [self.get(6, 16, 16, TILE_SIZE), self.get(7, 16, 16, TILE_SIZE)],
            [self.get(6, 18, 16, TILE_SIZE), self.get(7, 18, 16, TILE_SIZE)],
            [self.get(6, 17, 16, TILE_SIZE), self.get(7, 17, 16, TILE_SIZE)],
            [self.get(6, 15, 16, TILE_SIZE), self.get(7, 15, 16, TILE_SIZE)],
        ]

        self.SHEEP = [
            [self.get(9, 16, 16, TILE_SIZE), self.get(10, 16, 16, TILE_SIZE)],
            [self.get(9, 18, 16, TILE_SIZE), self.get(10, 18, 16, TILE_SIZE)],
            [self.get(9, 17, 16, TILE_SIZE), self.get(10, 17, 16, TILE_SIZE)],
            [self.get(9, 15, 16, TILE_SIZE), self.get(10, 15, 16, TILE_SIZE)],
        ]


        self.GHOST_PIG = [
            [self.get(6, 21, 16, TILE_SIZE), self.get(7, 21, 16, TILE_SIZE)],
            [self.get(6, 23, 16, TILE_SIZE), self.get(7, 23, 16, TILE_SIZE)],
            [self.get(6, 22, 16, TILE_SIZE), self.get(7, 22, 16, TILE_SIZE)],
            [self.get(6, 20, 16, TILE_SIZE), self.get(7, 20, 16, TILE_SIZE)],
        ]

        self.GHOST_SHEEP = [
            [self.get(9, 21, 16, TILE_SIZE), self.get(10, 21, 16, TILE_SIZE)],
            [self.get(9, 23, 16, TILE_SIZE), self.get(10, 23, 16, TILE_SIZE)],
            [self.get(9, 22, 16, TILE_SIZE), self.get(10, 22, 16, TILE_SIZE)],
            [self.get(9, 20, 16, TILE_SIZE), self.get(10, 20, 16, TILE_SIZE)],
        ]
