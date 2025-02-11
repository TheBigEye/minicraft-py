""" The gamelay speed is dependent for this """
GAME_TICKS: float = 32.0 # Yeah, i sucks making games

# NOTE: The original Minicraft uses "HEIGHT as 120 * 3" and "WIDTH as 160 * 3"

# Game window dimensions
SCREEN_WIDTH: int = 960
SCREEN_HEIGHT: int = 540

SCREEN_SIZE: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN_HALF: tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# World render distance (by chunks)
RENDER_WIDTH: int = 2
RENDER_HEIGHT: int = 2

RENDER_SIZE: tuple[int, int] = (RENDER_WIDTH, RENDER_HEIGHT)

# NOT CHANGE THESE (OR EVERYTHING WILL BROKE, lol)

TILE_SCALE: int = 2

TILE_SIZE: int = 32 # Each tile are 32x32 pixels
TILE_HALF: int = TILE_SIZE // 2
TILE_MULT: int = TILE_SIZE + TILE_HALF

CHUNK_SIZE: int = 8 # Each chunk is 8x8 tiles

POSITION_SHIFT = 4
TILE_BITS = 1 << POSITION_SHIFT  # 16 pixels = 1 tile

SCREEN_HALF_W: int = SCREEN_WIDTH // 2
SCREEN_HALF_H: int = SCREEN_HEIGHT // 2

DIRECTIONS = {
    ( 0,  1), # South
    ( 1,  0), # East
    ( 0, -1), # North
    (-1,  0), # West
}
