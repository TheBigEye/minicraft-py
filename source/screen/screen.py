from source.screen.sprites import Sprites

class Color:
    WHITE: tuple     = (255, 255, 255)
    GREY: tuple      = (128, 128, 128)
    DARK_GREY: tuple = (64,  64,  64 )
    RED: tuple       = (255, 000, 000)
    GREEN: tuple     = (000, 255, 000)
    BLUE: tuple      = (000, 000, 255)
    BLACK: tuple     = (000, 000, 000)
    CYAN: tuple      = (000, 255, 255)
    YELLOW: tuple    = (255, 255, 000)
    MAGENTA: tuple   = (255, 000, 255)
    DARK_RED: tuple  = (128, 000, 000)
    DARK_GREEN: tuple= (000, 128, 000)
    DARK_BLUE: tuple = (000, 000, 128)


class Screen:

    @staticmethod
    def draw_box(x, y, width, height):
        sprites = []

        for yy in range(y, y + height):
            for xx in range(x, x + width):

                if xx == x and yy == y:
                    sprites.append((Sprites.GUI_TOP_LEFT_CORNER, (xx * 16, yy * 16)))
                elif xx == x + width - 1 and yy == y:
                    sprites.append((Sprites.GUI_TOP_RIGHT_CORNER, (xx * 16, yy * 16)))
                elif xx == x and yy == y + height - 1:
                    sprites.append((Sprites.GUI_BOTTOM_LEFT_CORNER, (xx * 16, yy * 16)))
                elif xx == x + width - 1 and yy == y + height - 1:
                    sprites.append((Sprites.GUI_BOTTOM_RIGHT_CORNER, (xx * 16, yy * 16)))

                elif yy == y:
                    sprites.append((Sprites.GUI_TOP_BORDER, (xx * 16, yy * 16)))
                elif yy == y + height - 1:
                    sprites.append((Sprites.GUI_BOTTOM_BORDER, (xx * 16, yy * 16)))
                elif xx == x:
                    sprites.append((Sprites.GUI_LEFT_BORDER, (xx * 16, yy * 16)))
                elif xx == x + width - 1:
                    sprites.append((Sprites.GUI_RIGHT_BORDER, (xx * 16, yy * 16)))

                else:
                    sprites.append((Sprites.GUI_BACKGROUND, (xx * 16, yy * 16)))

        return sprites
