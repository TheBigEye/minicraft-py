import pygame

from source.utils.constants import TILE_SCALE, TILE_SIZE

from pygame.transform import flip

class Sprites:

    def __init__(self):
        self.atlas = pygame.image.load('assets/atlas.png').convert()
        self.atlas.set_colorkey((255, 0, 255))


    def initialize(self) -> None:
        """ Initialize all sprites """

        self.NULL = [self.get_tiled(0, 31, 16)]
        self.GREEN_EYE = self.get_tiled(0, 29, 16)
        self.A_POTATOE = self.get_tiled(1, 29, 16)
        self.HIGHLIGHT = self.get_tiled(1, 31, 16)

        # UI elements
        self.HEART_FULL = self.get_tiled(4, 62, 8)
        self.HEART_NONE = self.get_tiled(5, 62, 8)
        self.STAMINA_FULL = self.get_tiled(4, 63, 8)
        self.STAMINA_NONE = self.get_tiled(5, 63, 8)


        self.SMASH_PARTICLE = self.get_tiled(6, 31, 16)


        self.WATER_SWIM = [
            self.get_tiled(4, 31, 16),
            self.get_tiled(5, 31, 16),
        ]


        self.GUI = [
            self.get_tiled(7, 63, 8), # Background

            self.get_tiled(7, 62, 8), # Top border
            self.get_tiled(6, 63, 8), # Left border
            flip(self.get_tiled(6, 63, 8), True, False), # Right border
            flip(self.get_tiled(7, 62, 8), False, True), # Bottom border

            self.get_tiled(6, 62, 8), # Top-left corner
            flip(self.get_tiled(6, 62, 8), True, False), # Top-right corner
            flip(self.get_tiled(6, 62, 8), False, True), # Bottom-left corner
            flip(self.get_tiled(6, 62, 8), True,  True), # Bottom-right corner
        ]


        # Base terrain sprites
        self.GRASS = [
            self.get_tiled(1, 1, 16),  # Base grass

            self.get_tiled(1, 0, 16),  # Top transition
            self.get_tiled(2, 1, 16),  # Left transition
            self.get_tiled(0, 1, 16),  # Right transition
            self.get_tiled(1, 2, 16),  # Bottom transition

            self.get_tiled(0, 0, 16),  # Top-left corner
            self.get_tiled(2, 0, 16),  # Top-right corner
            self.get_tiled(0, 2, 16),  # Bottom-left corner
            self.get_tiled(2, 2, 16),  # Bottom-right corner

            self.get_tiled(1, 3, 16),  # Base grass 2
        ]

        self.FLOWERS = [
            self.get_tiled(0, 3, 16)
        ]

        self.HOLE = [
            self.get_tiled(4, 1, 16),  # Base hole

            self.get_tiled(4, 0, 16),  # Top transition
            self.get_tiled(5, 1, 16),  # Left transition
            self.get_tiled(3, 1, 16),  # Right transition
            self.get_tiled(4, 2, 16),  # Bottom transition

            self.get_tiled(3, 0, 16),  # Top-left corner
            self.get_tiled(5, 0, 16),  # Top-right corner
            self.get_tiled(3, 2, 16),  # Bottom-left corner
            self.get_tiled(5, 2, 16),  # Bottom-right corner
        ]

        self.SAND = [
            self.get_tiled(13, 1, 16), # Base sand

            self.get_tiled(13, 0, 16), # Top transition
            self.get_tiled(14, 1, 16), # Left transition
            self.get_tiled(12, 1, 16), # Right transition
            self.get_tiled(13, 2, 16), # Bottom transition

            self.get_tiled(12, 0, 16), # Top-left corner
            self.get_tiled(14, 0, 16), # Top-right corner
            self.get_tiled(12, 2, 16), # Bottom-left corner
            self.get_tiled(14, 2, 16), # Bottom-right corner

            self.get_tiled(12, 3, 16),
            self.get_tiled(13, 3, 16)
        ]

        self.SNOW = [
            self.get_tiled(7, 1, 16), # Base snow

            self.get_tiled(7, 0, 16), # Top transition
            self.get_tiled(8, 1, 16), # Left transition
            self.get_tiled(6, 1, 16), # Right transition
            self.get_tiled(7, 2, 16), # Bottom transition

            self.get_tiled(6, 0, 16), # Top-left corner
            self.get_tiled(8, 0, 16), # Top-right corner
            self.get_tiled(6, 2, 16), # Bottom-left corner
            self.get_tiled(8, 2, 16), # Bottom-right corner

            self.get_tiled(6, 3, 16), # Base snow 2
        ]

        self.ICE = [
            self.get_tiled(10, 1, 16), # Base ice

            self.get_tiled(10, 0, 16), # Top transition
            self.get_tiled(11, 1, 16), # Left transition
            self.get_tiled(9, 1, 16),  # Right transition
            self.get_tiled(10, 2, 16), # Bottom transition

            self.get_tiled(9, 0, 16),  # Top-left corner
            self.get_tiled(11, 0, 16), # Top-right corner
            self.get_tiled(9, 2, 16),  # Bottom-left corner
            self.get_tiled(11, 2, 16), # Bottom-right corner

            self.get_tiled(10, 3, 16), # Base ice 2
            self.get_tiled(10, 3, 16), # Base ice 3
        ]


        self.ICEBERG = [
            self.get_tiled(9, 3, 16),
            self.get_tiled(11, 3, 16)
        ]

        self.CACTUS = [
            self.get_tiled(3, 5, 16),
            self.get_tiled(3, 6, 16)
        ]


        self.IRON_ORE = [
            self.get_tiled(0, 5, 16)
        ]



        self.WATER = [
            self.get_tiled(16, 1, 16), # Base water

            self.get_tiled(16, 0, 16), # Top transition
            self.get_tiled(17, 1, 16), # Left transition
            self.get_tiled(15, 1, 16),  # Right transition
            self.get_tiled(16, 2, 16), # Bottom transition

            self.get_tiled(15, 0, 16),  # Top-left corner
            self.get_tiled(17, 0, 16), # Top-right corner
            self.get_tiled(15, 2, 16),  # Bottom-left corner
            self.get_tiled(17, 2, 16), # Bottom-right corner

            self.get_tiled(15, 3, 16), # Base water 2
            self.get_tiled(16, 3, 16), # Base water 3
        ]

        self.STONE = [
            self.get_tiled(19, 1, 16), # Base stone

            self.get_tiled(19, 0, 16), # Top transition
            self.get_tiled(20, 1, 16), # Left transition
            self.get_tiled(18, 1, 16), # Right transition
            self.get_tiled(19, 2, 16), # Bottom transition

            self.get_tiled(18, 0, 16), # Top-left corner
            self.get_tiled(20, 0, 16), # Top-right corner
            self.get_tiled(18, 2, 16), # Bottom-left corner
            self.get_tiled(20, 2, 16), # Bottom-right corner

            self.get_tiled(18, 3, 16), # Base stone variant 2
            self.get_tiled(19, 3, 16), # Base stone variant 3

            self.get_tiled(6, 5, 16), # Top-left inner-corner
            self.get_tiled(7, 5, 16), # Top-right inner-corner
            self.get_tiled(6, 6, 16), # Bottom-left inner-corner
            self.get_tiled(7, 6, 16), # Bottom-right inner-corner
        ]

        self.DIRT = [
            self.get_tiled(3, 3, 16),
            self.get_tiled(4, 3, 16)
        ]

        # Tree sprites
        self.OAK_TREE = [
            self.get_tiled(0, 4, 32),
            self.get_tiled(1, 4, 32)
        ]

        self.BIRCH_TREE = [
            self.get_tiled(0, 5, 32),
            self.get_tiled(0, 5, 32),
        ]

        self.PINE_TREE = [
            self.get_tiled(0, 6, 32),
            self.get_tiled(1, 6, 32)
        ]


        self.WORKBENCH = self.get_tiled(0, 25, 16)
        self.ANVIL = self.get_tiled(1, 25, 16)
        self.ENCHANTER = self.get_tiled(2, 25, 16)
        self.OVEN = self.get_tiled(3, 25, 16)
        self.FURNACE = self.get_tiled(4, 25, 16)
        self.CHEST = self.get_tiled(5, 25, 16)


        # Player sprites [down, left, right, up]
        self.PLAYER = [
            [self.get_tiled(0, 16, 16), self.get_tiled(1, 16, 16)],
            [self.get_tiled(0, 18, 16), self.get_tiled(1, 18, 16)],
            [self.get_tiled(0, 17, 16), self.get_tiled(1, 17, 16)],
            [self.get_tiled(0, 15, 16), self.get_tiled(1, 15, 16)],
        ]

        self.VAMP = [
            [self.get_tiled(3, 16, 16), self.get_tiled(4, 16, 16)],
            [self.get_tiled(3, 18, 16), self.get_tiled(4, 18, 16)],
            [self.get_tiled(3, 17, 16), self.get_tiled(4, 17, 16)],
            [self.get_tiled(3, 15, 16), self.get_tiled(4, 15, 16)],
        ]

        self.ZOMBIE = [
            [self.get_tiled(3, 21, 16), self.get_tiled(4, 21, 16)],
            [self.get_tiled(3, 23, 16), self.get_tiled(4, 23, 16)],
            [self.get_tiled(3, 22, 16), self.get_tiled(4, 22, 16)],
            [self.get_tiled(3, 20, 16), self.get_tiled(4, 20, 16)],
        ]

        self.PIG = [
            [self.get_tiled(6, 16, 16), self.get_tiled(7, 16, 16)],
            [self.get_tiled(6, 18, 16), self.get_tiled(7, 18, 16)],
            [self.get_tiled(6, 17, 16), self.get_tiled(7, 17, 16)],
            [self.get_tiled(6, 15, 16), self.get_tiled(7, 15, 16)],
        ]

        self.SHEEP = [
            [self.get_tiled(9, 16, 16), self.get_tiled(10, 16, 16)],
            [self.get_tiled(9, 18, 16), self.get_tiled(10, 18, 16)],
            [self.get_tiled(9, 17, 16), self.get_tiled(10, 17, 16)],
            [self.get_tiled(9, 15, 16), self.get_tiled(10, 15, 16)],
        ]

        self.GHOST_PIG = [
            [self.get_tiled(6, 21, 16), self.get_tiled(7, 21, 16)],
            [self.get_tiled(6, 23, 16), self.get_tiled(7, 23, 16)],
            [self.get_tiled(6, 22, 16), self.get_tiled(7, 22, 16)],
            [self.get_tiled(6, 20, 16), self.get_tiled(7, 20, 16)],
        ]

        self.GHOST_SHEEP = [
            [self.get_tiled(9, 21, 16), self.get_tiled(10, 21, 16)],
            [self.get_tiled(9, 23, 16), self.get_tiled(10, 23, 16)],
            [self.get_tiled(9, 22, 16), self.get_tiled(10, 22, 16)],
            [self.get_tiled(9, 20, 16), self.get_tiled(10, 20, 16)],
        ]


    def get_tiled(self, x: int, y: int, size) -> pygame.Surface:
        """ Extract and scale a sprite from the atlas """
        scale = size * TILE_SCALE
        return pygame.transform.scale(
            self.atlas.subsurface((x * size, y * size, size, size)), (scale, scale)
        )


    def get_px(self, x: int, y: int, width: int, height: int, scale: int) -> pygame.Surface:
        """ Extract and scale a sprite from the atlas """
        return pygame.transform.scale(
            self.atlas.subsurface((x, y, width, height)), (scale, scale)
        )
