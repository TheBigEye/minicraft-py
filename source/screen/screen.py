from source.screen.sprites import Sprites

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
