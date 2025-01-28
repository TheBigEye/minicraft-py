from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from source.core.game import Game
    from source.screen.screen import Screen


class Menu:

    def initialize(self, game: Game) -> None:
        self.game = game

    def update(self) -> None:
        pass


    def render(self, screen: Screen) -> None:
        pass
