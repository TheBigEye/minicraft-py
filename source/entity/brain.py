from __future__ import annotations

import heapq
from enum import IntEnum
from random import uniform
from math import hypot, pi, cos, sin
from typing import TYPE_CHECKING

from pygame import Vector2
from source.utils.autoslots import auto_slots
from source.utils.constants import DIRECTIONS

if TYPE_CHECKING:
    from source.entity.mob.mob import Mob
    from source.world.tile import Tile
    from source.world.world import World


class State(IntEnum):
    IDLE    = 0
    MOVING  = 1
    WAITING = 2
    CHASING = 3


@auto_slots
class Brain:
    def __init__(self, mob: Mob):
        self.mob: Mob = mob # Reference to the mob
        self.state: State = State.IDLE # Initially, mob is idle
        self.target_pos: Vector2 = Vector2(0, 0) # No target yet

        self.base_speed: float = self.mob.speed

        self.path: list[Vector2] = []

    def update(self, world: World) -> None:
        pass


    def valid_position(self, world: World, x: float, y: float) -> bool:
        # Check current tile ...
        tile: Tile = world.get_tile(int(x), int(y))
        if not tile or tile.solid or tile.liquid:
            return False

        # Only check adjacent tiles
        for dx, dy in DIRECTIONS:
            check_x = int(x) + dx
            check_y = int(y) + dy

            nearby: Tile = world.get_tile(check_x, check_y)
            if not nearby or nearby.solid:
                return False

        return True


    def interpolate(self, path: list[Vector2]) -> list[Vector2]:
        """Add intermediate points between each tile in the path for smoother movement"""
        if len(path) < 2:
            return path

        interpolated: list[Vector2] = []

        for i in range(len(path) - 1):
            current = path[i]
            next_point = path[i + 1]

            # Add current point
            interpolated.append(current)

            # Calculate 3 intermediate points between current and next
            for t in [0.25, 0.5, 0.75]:
                intermediate = Vector2(
                    current.x + (next_point.x - current.x) * t,
                    current.y + (next_point.y - current.y) * t
                )
                interpolated.append(intermediate)

        # Add the final point
        interpolated.append(path[-1])
        return interpolated


    def find_path(self, world: World, start: Vector2, end: Vector2) -> list[Vector2]:
        start_pos: tuple[int, int] = (int(start.x), int(start.y))
        end_pos: tuple[int, int] = (int(end.x), int(end.y))

        # Check if the start position is in a loaded chunk
        if not world.get_tile(start_pos[0], start_pos[1]):
            return []

        # Check if the final position is valid, else find nearest valid position
        if not self.valid_position(world, end_pos[0], end_pos[1]):
            best_pos = None
            min_distance = float('inf')

            # Search on an circular pattern
            for angle in range(0, 360, 45):
                for dist in range(1, 4):
                    dx = int(cos(angle * pi / 180) * dist)
                    dy = int(sin(angle * pi / 180) * dist)
                    test_pos = (end_pos[0] + dx, end_pos[1] + dy)

                    if world.get_tile(test_pos[0], test_pos[1]) and self.valid_position(world, test_pos[0], test_pos[1]):
                        current_dist = hypot(dx, dy) # Euclidean distance

                        if current_dist < min_distance:
                            min_distance = current_dist
                            best_pos = test_pos

            if not best_pos:
                return [] # No valid path found
            end_pos = best_pos

        # A* implementation :D
        frontier: list = [(0, start_pos)]
        came_from: dict = {start_pos: None}
        cost_so_far: dict = {start_pos: 0}

        while frontier:
            # Get the next position to explore
            _, current = heapq.heappop(frontier) # Pop the tile with the lowest cost

            # We've found the goal
            if current == end_pos:
                break

            # Explore all adjacent tiles (on any direction)
            for angle in range(0, 360, 45):
                dx = round(cos(angle * pi / 180))
                dy = round(sin(angle * pi / 180))
                next_pos = (current[0] + dx, current[1] + dy)

                # Check if next position is in a loaded chunk
                if not world.get_tile(next_pos[0], next_pos[1]) or not self.valid_position(world, next_pos[0], next_pos[1]):
                    continue

                movement_cost = hypot(dx, dy)
                new_cost: float = cost_so_far[current] + movement_cost

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority: float = new_cost + hypot(end_pos[0] - next_pos[0], end_pos[1] - next_pos[1])

                    # The priority queue: less steps = higher priority
                    heapq.heappush(frontier, (priority, next_pos))

                    came_from[next_pos] = current

        # Rebuild the path
        if end_pos not in came_from:
            return []

        path: list[Vector2] = []
        current = end_pos
        while current and current != start_pos:
            path.append(Vector2(current[0], current[1]))
            current = came_from[current]
        path.reverse()

        # Add intermediate points for smoother movement
        return self.interpolate(path)

    def water_between(self, world: World, start: Vector2, end: Vector2) -> bool:
        """
        Check if there's water between two points using Bresenham's line algorithm.
        This algorithm traces a virtual line between start and end points, checking each tile.
        """
        # Convert Vector2 coordinates to integers
        x1, y1 = int(start.x), int(start.y)
        x2, y2 = int(end.x), int(end.y)

        # Calculate the distance in X and Y between points
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1

        # Determine movement direction (1 or -1)
        sx = 1 if x2 > x1 else -1  # X direction
        sy = 1 if y2 > y1 else -1  # Y direction

        # If X distance is greater, prioritize horizontal movement
        if dx > dy:
            err = dx / 2.0  # Initial error for Bresenham
            while x != x2:  # Until we reach the end point in X
                # Check if current tile is water
                tile = world.get_tile(x, y)
                if tile and tile.liquid:
                    return True  # Found water, terminate

                # Update error and Y position if needed
                err -= dy
                if err < 0:
                    y += sy      # Move in Y
                    err += dx    # Readjust error
                x += sx  # Always move in X

        # If Y distance is greater, prioritize vertical movement
        else:
            err = dy / 2.0  # Initial error for Bresenham
            while y != y2:  # Until we reach the end point in Y
                # Check if current tile is water
                tile = world.get_tile(x, y)
                if tile and tile.liquid:
                    return True  # Found water, terminate

                # Update error and X position if needed
                err -= dx
                if err < 0:
                    x += sx      # Move in X
                    err += dy    # Readjust error
                y += sy  # Always move in Y

        # If we get here, no water was found in the path
        return False


@auto_slots
class PassiveBrain(Brain):
    def __init__(self, mob: Mob):
        super().__init__(mob)

        self.path_timer = 0
        self.last_pos = self.mob.position

        self.wander_timer: int = 30 # Time between wandering
        self.wander_cooldown: int = 70 # Cooldown after wandering

        # Threshold to consider that we have reached the destination
        self.move_threshold: float = 0.1


    def update(self, world: World) -> None:
        self.mob.speed = self.base_speed

        if self.state == State.IDLE:
            self.wander_timer += 1
            if self.wander_timer >= self.wander_cooldown:
                self.random_target(world)
                self.wander_timer = 0

        elif self.state == State.MOVING:
            self.path_timer += 1

            if not (self.path_timer % 75 == 0):
                if not self.valid_position(world, self.target_pos.x, self.target_pos.y):
                    self.random_target(world)
                    return

            self.last_pos = self.mob.position

            # We move directly towards the goal
            self.mob.move(world, self.target_pos.x, self.target_pos.y)

            # Stuck check
            if (self.path_timer % 75 == 0):
                if self.last_pos == self.mob.position:
                    self.random_target(world)
                    self.path_timer = 0

            # If we are very close to the goal, we consider that we have finished
            if abs(self.mob.position.x - self.target_pos.x) < self.move_threshold and \
               abs(self.mob.position.y - self.target_pos.y) < self.move_threshold:
                self.state = State.IDLE


    def random_target(self, world: World) -> None:
        # Try up to 10 random spots
        for _ in range(10):
            # We choose an random spot using a radius
            angle = uniform(0, 2 * pi)
            dist = uniform(2, 4) # Random distance
            new_x = self.mob.position.x + cos(angle) * dist
            new_y = self.mob.position.y + sin(angle) * dist

            # Check both valid position and no water between points
            if (self.valid_position(world, new_x, new_y) and
                not self.water_between(world, self.mob.position, Vector2(new_x, new_y))):
                self.target_pos = Vector2(new_x, new_y)
                self.state = State.MOVING
                return

        # If we can't find a good spot, we'll just stand still
        self.state = State.IDLE


@auto_slots
class HostileBrain(Brain):
    def __init__(self, mob: Mob):
        super().__init__(mob)
        self.path_timer: int = 0

        # The range (in tiles) within which the mob will start chasing
        self.path_range: float = 4.50

        # Minimal distance to the player
        self.target_dist: float = 0.40

        # How often the mob will update its path (ticks)
        self.update_rate: int = 10

        # Threshold to consider that we have reached the destination
        self.move_threshold: float = 0.1

        self.passive_brain = PassiveBrain(mob)


    def update(self, world: World) -> None:
        player_pos = world.player.position
        player_dist = self.mob.position.distance_to(player_pos)

        self.mob.speed = self.base_speed * 1.5

        # If we’re close to the player, STOP
        if player_dist <= self.target_dist:
            self.state = State.WAITING
            return

        # Start chasing if the player is within range and not swimming
        if (player_dist <= self.path_range and
            not world.player.swimming() and
            not self.water_between(world, self.mob.position, player_pos)):
            self.path_timer += 1
            if self.path_timer >= self.update_rate or not self.path:
                self.path = self.find_path(world, self.mob.position, player_pos)
                self.path_timer = 0

                if not self.path:
                    self.state = State.IDLE
                    return

                self.state = State.CHASING

            if self.state == State.CHASING and self.path:
                next_point: Vector2 = self.path[0]

                if not self.valid_position(world, next_point.x, next_point.y):
                    self.path = self.find_path(world, self.mob.position, player_pos)

                    # If no path, well, let’s wander
                    if not self.path:
                        self.state = State.IDLE
                        self.passive_brain.update(world)
                        return

                # We move directly to the next point
                self.mob.move(world, next_point.x, next_point.y)

                # We check if we reach the point using the threshold
                if abs(self.mob.position.x - next_point.x) < self.move_threshold and \
                   abs(self.mob.position.y - next_point.y) < self.move_threshold:
                    self.path.pop(0) # Move to the next point
        else:
            # If we're not chasing, let's just wander randomly
            self.state = State.MOVING
            self.passive_brain.update(world)


@auto_slots
class NeutralBrain(Brain):
    def __init__(self, mob: Mob):
        super().__init__(mob)
        self.path_timer: int = 0

        # The range (in tiles) within which the mob will detect player
        self.path_range: float = 4.50

        # Minimal distance to the player
        self.target_dist: float = 0.40

        # How often the mob will update its path (ticks)
        self.update_rate: int = 10

        self.move_threshold: float = 0.1

        # For movement detection
        self.last_target: Vector2 = None

        # Memory
        self.memory_time: int = 16 # How long to remember player movement
        self.current_memory: int = 0 # Current memory counter

        # Waiting period after memory expires
        self.wait_time: int = 12 # How long to wait before wandering
        self.current_wait: int = 0 # Current wait counter

        # Use PassiveBrain for wandering behavior
        self.passive_brain = PassiveBrain(mob)


    def update(self, world: World) -> None:
        player_pos = world.player.position
        player_dist = self.mob.position.distance_to(player_pos)

        # Check if player is moving
        target_moving = False
        if self.last_target:
            target_moving = player_pos != self.last_target
        self.last_target = Vector2(player_pos)

        # Update memory
        if target_moving:
            self.current_memory = self.memory_time
            self.current_wait = 0 # Reset wait timer if player moves
        elif self.current_memory > 0:
            self.current_memory -= 1
            if self.current_memory == 0: # Memory just ran out
                self.current_wait = self.wait_time # Start waiting period

        # Default speed for neutral mobs
        self.mob.speed = self.base_speed

        # Default speed for neutral mobs
        if player_dist <= self.target_dist:
            self.state = State.WAITING
            return

        # Chase if player is within range and either moving or remembered as moving
        if (player_dist <= self.path_range and
            (target_moving or self.current_memory > 0) and
            not world.player.swimming() and
            not self.water_between(world, self.mob.position, player_pos)):

            # Increase speed while chasing
            self.mob.speed = self.base_speed * 2.00

            self.path_timer += 1
            if self.path_timer >= self.update_rate or not self.path:
                self.path = self.find_path(world, self.mob.position, player_pos)
                self.path_timer = 0

                if not self.path:
                    self.state = State.IDLE
                    return

                self.state = State.CHASING

            if self.state == State.CHASING and self.path:
                next_point: Vector2 = self.path[0]

                if not self.valid_position(world, next_point.x, next_point.y):
                    self.path = self.find_path(world, self.mob.position, player_pos)

                    if not self.path:
                        self.state = State.IDLE
                        self.passive_brain.update(world)
                        return

                self.mob.move(world, next_point.x, next_point.y)

                if abs(self.mob.position.x - next_point.x) < self.move_threshold and \
                   abs(self.mob.position.y - next_point.y) < self.move_threshold:
                    self.path.pop(0)
        else:
            # Check if we should wait or move
            if self.current_wait > 0:
                self.current_wait -= 1
                self.state = State.WAITING
            else:
                # If waiting period is over and no player movement ...
                self.state = State.MOVING
                self.passive_brain.update(world)
