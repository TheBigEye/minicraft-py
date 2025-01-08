
""" The gamelay speed is dependent for this """
GAME_TICKS: float = 30.0 # Yeah, i sucks making games

# NOTE: The original Minicraft uses "HEIGHT as 120 * 3" and "WIDTH as 160 * 3"

SCREEN_FULL_H: int = 540
SCREEN_FULL_W: int = 960


RENDER_RANGE_V: int = 2
RENDER_RANGE_H: int = 2


POSITION_SHIFT = 4
TILE_BITS = 1 << POSITION_SHIFT  # 16 pixels = 1 tile


# NOT CHANGE THESE (OR EVERYTHING WILL BROKE, lol)

TILE_SIZE: int = 32
CHUNK_SIZE: int = 8

SCREEN_HALF_W: int = SCREEN_FULL_W // 2
SCREEN_HALF_H: int = SCREEN_FULL_H // 2

TILE_HALF_SIZE: int = TILE_SIZE // 2
TILE_MULT_SIZE: int = TILE_SIZE + TILE_HALF_SIZE

SCREEN_SIZE_T: tuple = (SCREEN_FULL_W, SCREEN_FULL_H)
SCREEN_SIZE_I: int = (SCREEN_FULL_W * SCREEN_FULL_H)
