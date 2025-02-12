from source.entity.entity import Entity
from source.screen.screen import Screen
from source.utils.constants import SCREEN_HALF, TILE_SIZE

class Particle(Entity):

    def __init__(self) -> None:
        super().__init__()

        # This avoids loading particles
        # from Saveload :D
        self.eid = -1

        self.rx = 0
        self.ry = 0

        self.tick_time: int = 0


    def update(self) -> None:
        self.rx = int(SCREEN_HALF[0] - ((self.world.player.position.x - self.position.x) * TILE_SIZE))
        self.ry = int(SCREEN_HALF[1] - ((self.world.player.position.y - self.position.y) * TILE_SIZE))


    def render(self, screen: Screen) -> None:
        pass
