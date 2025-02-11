from __future__ import annotations

from random import choice
from typing import TYPE_CHECKING

from pygame import Surface

from source.entity.particle.smash import SmashParticle
from source.entity.particle.text import TextParticle
from source.screen.color import Color
from source.utils.constants import TILE_HALF, TILE_SIZE
from source.utils.autoslots import auto_slots

if TYPE_CHECKING:
    from source.world.world import World


@auto_slots
class Tile:

    def __init__(self, id: int, sprites: list[Surface], solid: bool, liquid: bool, parent: int, health: int) -> None:
        self.id = id
        self.solid = solid
        self.liquid = liquid
        self.parent = parent
        self.health = health

        self.sprites = sprites
        self.sprite = None

        if not self.sprite:
            # We check if are a Tree model
            if len(self.sprites) == 2:
                self.sprite = choice(self.sprites)

            # Or a normal tile model
            elif len(self.sprites) >= 9:
                # Get available base sprites (first one and any after index 8)
                base_sprites = [self.sprites[0]] + self.sprites[9:11]
                # Randomly select one of the base variations
                self.sprite = choice(base_sprites)

            # else ...
            else:
                self.sprite = self.sprites[0]

        self.connectors = []


    def hurt(self, world: World, x: int, y: int, damage: int) -> None:
        if self.health > 0:
            self.health -= damage

            world.game.sound.play("genericHurt")

            if self.solid:
                world.add(SmashParticle(x, y))
                world.add(TextParticle(str(damage), x + 0.40, y + 0.40, Color.RED))

            if (self.health <= 0) and (self.parent > -1):
                world.set_tile(x, y, self.parent)


    def render(self, world: World, x: int, y: int) -> None:
        """
        Renderiza el tile de forma que la parte inferior del sprite se alinee con la
        posición (x, y). Para sprites grandes (por ejemplo, árboles), se usa un
        anclaje de tipo “bottom center”.
        """
        # Si el sprite es mayor que el tamaño base del tile, se asume que es un sprite grande.
        if self.sprite.get_width() > TILE_SIZE:
            sprite_width = self.sprite.get_width()
            sprite_height = self.sprite.get_height()
            # Se centra horizontalmente: se toma el centro del tile (x + TILE_HALF)
            # y se le resta la mitad del ancho del sprite.
            draw_x = (x + TILE_HALF) - (sprite_width / 2)
            # Se alinea verticalmente para que la parte inferior del sprite coincida con y.
            draw_y = y - (sprite_height - TILE_SIZE) + 4
            # El tercer valor (por ejemplo, y+2) es el z-index para el orden de dibujo.
            world.surfaces.append((self.sprite, (draw_x, draw_y, y - 4)))
            return

        # Para sprites que no son “grandes” se puede mantener el comportamiento original.
        # Si lo deseas, también podrías ajustar su alineación para que queden "pegados al suelo":
        world.surfaces.append((self.sprite, (x, y, -24)))
        # Se agregan los conectores (por ejemplo, para transiciones) sin modificar su posición.
        for sprite in self.connectors:
            world.surfaces.append((sprite, (x, y, -24)))


    def clone(self) -> Tile:
        """ Returns a copy of the tile instance """
        return self.__class__(self.id, self.sprites, self.solid, self.liquid, self.parent, self.health)
