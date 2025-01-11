from __future__ import annotations

import heapq
from enum import Enum
from random import choice, randint
from typing import TYPE_CHECKING

from pygame import Vector2

if TYPE_CHECKING:
    from source.entity.mob import Mob
    from source.level.tile import Tile
    from source.level.world import World


class State(Enum):
    IDLE    = 0
    MOVING  = 1
    WAITING = 2
    CHASING = 3


class Brain:
    def __init__(self, mob: Mob):
        self.mob = mob
        self.state = State.IDLE
        self.target_pos = Vector2(0, 0)

        # Distance for avoid solid tiles or obstacles from path
        self.safety_distance = 0.80

        self.directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0)
        ]

    def update(self, world: World) -> None:
        pass

    # NOTE: debug this
    def valid_position(self, world: World, x: float, y: float) -> bool:
        # Check current tile ...
        tile: Tile = world.get_tile(int(x), int(y))
        if tile is None or tile.solid or tile.liquid:
            return False

        # Only check adjacent tiles
        for dx, dy in self.directions:
            check_x = int(x) + dx
            check_y = int(y) + dy

            nearby: Tile = world.get_tile(check_x, check_y)
            if nearby is None or nearby.solid or nearby.liquid:
                return False

        return True


    def find_path(self, world: World, start: Vector2, end: Vector2) -> list:
        start_pos = (int(start.x), int(start.y))
        end_pos = (int(end.x), int(end.y))

        # First check if start position is in a loaded chunk
        if world.get_tile(start_pos[0], start_pos[1]) is None:
            return []

        # Check if the final position is valid, else find nearest valid position
        if not self.valid_position(world, end_pos[0], end_pos[1]):
            best_pos = None
            min_distance = float('inf')

            # Search in a cross pattern
            for dist in range(1, 4):
                for dx, dy in [(dist, 0), (-dist, 0), (0, dist), (0, -dist)]:
                    test_pos = (end_pos[0] + dx, end_pos[1] + dy)
                    if world.get_tile(test_pos[0], test_pos[1]) is not None and \
                    self.valid_position(world, test_pos[0], test_pos[1]):
                        current_dist = abs(dx) + abs(dy)  # Manhattan distance
                        if current_dist < min_distance:
                            min_distance = current_dist
                            best_pos = test_pos

            if best_pos is None:
                return []
            end_pos = best_pos

        # A* implementation :D
        frontier = [(0, start_pos)]
        came_from = {start_pos: None}
        cost_so_far = {start_pos: 0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == end_pos:
                break

            for dx, dy in self.directions:
                # NOTE: debug this
                next_pos = (current[0] + dx, current[1] + dy)

                # Check if next position is in a loaded chunk
                if world.get_tile(next_pos[0], next_pos[1]) is None or \
                not self.valid_position(world, next_pos[0], next_pos[1]):
                    continue

                new_cost = cost_so_far[current] + 1 # Cost is always 1

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + abs(end_pos[0] - next_pos[0]) + abs(end_pos[1] - next_pos[1])
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Rebuild the path
        if end_pos not in came_from:
            return []

        path = []
        current = end_pos
        while current and current != start_pos:
            path.append(Vector2(current[0], current[1]))
            current = came_from[current]
        path.reverse()
        return path


class PassiveBrain(Brain):
    def __init__(self, mob: Mob):
        super().__init__(mob)
        self.wander_timer = 30
        self.wander_cooldown = 60


    def update(self, world: World) -> None:
        if self.state == State.IDLE:
            self.wander_timer += 1
            if self.wander_timer >= self.wander_cooldown:
                self.random_target(world)
                self.wander_timer = 0

        elif self.state == State.MOVING:
            if not self.valid_position(world, self.target_pos.x, self.target_pos.y):
                self.random_target(world)
                return

            path = self.find_path(world, self.mob.position, self.target_pos)
            if not path:
                self.random_target(world)
                return

            next_pos = path[0]
            self.mob.move(world, next_pos.x, next_pos.y)
            if self.mob.position.distance_to(self.target_pos) < 0.50:
                self.state = State.IDLE


    def random_target(self, world: World) -> None:
        for _ in range(10):
            direction = choice(self.directions)
            dist = randint(2, 4)
            new_x = self.mob.position.x + direction[0] * dist
            new_y = self.mob.position.y + direction[1] * dist

            if self.valid_position(world, new_x, new_y):
                self.target_pos = Vector2(new_x, new_y)
                self.state = State.MOVING
                return

        self.state = State.IDLE


class HostileBrain(Brain):
    def __init__(self, mob: Mob):
        super().__init__(mob)
        self.state = State.IDLE

        self.path = []
        self.path_timer = 0
        self.path_range = 4.50

        self.target_dist = 0.50
        self.update_rate = 10

        self.passive_brain = PassiveBrain(mob)


    def update(self, world: World) -> None:
        # BUG BUG: There is something here that can freeze the game
        # randomly, probably the algorithm is trying to trace an
        # impossible path and that must be hanging the CPU

        player_pos = world.player.position
        player_dist = self.mob.position.distance_to(player_pos)

        if player_dist <= self.path_range:
            if player_dist <= self.target_dist:
                self.state = State.WAITING
                return

            self.path_timer += 1
            if self.path_timer >= self.update_rate or not self.path:
                self.path = self.find_path(world, self.mob.position, player_pos)
                self.path_timer = 0

                if not self.path:
                    self.state = State.IDLE
                    self.passive_brain.update(world)
                    return

                self.state = State.CHASING

            if self.state == State.CHASING and self.path:
                next_point = self.path[0]
                if not self.valid_position(world, next_point.x, next_point.y):
                    self.path = self.find_path(world, self.mob.position, player_pos)
                    if not self.path:
                        self.state = State.IDLE
                        self.passive_brain.update(world)
                        return

                self.mob.move(world, next_point.x, next_point.y)
                if self.mob.position.distance_to(next_point) < 0.50:
                    self.path.pop(0)

        else:
            self.state = State.MOVING
            self.passive_brain.update(world)
