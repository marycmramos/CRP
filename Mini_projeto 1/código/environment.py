from typing import List, Set
from utils import MOVES
import random

class Environment:
    def __init__(self, w, h, walls, pellets, start_pos):
        self.w, self.h = w, h
        self.walls = set(walls)
        self.pellets = set(pellets)
        self.pacman_pos = start_pos
        self.start_pos = start_pos

        self.time = 0
        self.finished = False
        self.over = False

        self.lives = 3
        self.score = 0

        self.ghosts: List = []

    def in_bounds(self, c):
        x, y = c
        return 0 <= x < self.w and 0 <= y < self.h

    def blocked(self, c):
        return (not self.in_bounds(c)) or c in self.walls

    def step(self, action, move_ghosts=True):
        if self.finished or self.over:
            return

        self.time += 1

        if action in MOVES:
            dx, dy = MOVES[action]
            nxt = (self.pacman_pos[0]+dx, self.pacman_pos[1]+dy)
            if not self.blocked(nxt):
                self.pacman_pos = nxt

        for g in self.ghosts:
            if g.pos == self.pacman_pos:
                self.kill_pacman()
                return

        if self.pacman_pos in self.pellets:
            self.pellets.remove(self.pacman_pos)
            self.score += 10

        if move_ghosts:
            for g in self.ghosts:
                g.perceive_and_update(self)
                act = g.choose_action(self)
                g.step(act, self)

                if g.pos == self.pacman_pos:
                    self.kill_pacman()
                    return

        if len(self.pellets) == 0:
            self.finished = True


    def kill_pacman(self):
        self.lives -= 1
        self.pacman_pos = self.start_pos
        if self.lives <= 0:
            self.over = True


    def render(self):
        buf = []
        buf.append(f"t={self.time} | score={self.score} | lives={self.lives} | pellets={len(self.pellets)}")

        for y in range(self.h):
            row = ""
            for x in range(self.w):
                c = (x, y)
                
                if c == self.pacman_pos:
                    row += "P"
                elif any(g.pos == c for g in self.ghosts):
                    idx = next(i for i, g in enumerate(self.ghosts) if g.pos == c)
                    row += str(idx+1)
                elif c in self.walls:
                    row += "#"
                elif c in self.pellets:
                    row += "."
                else:
                    row += " "
            buf.append(row)

        if self.finished:
            buf.append("*** YOU WON! ***")

        if self.over:
            buf.append("*** GAME OVER ***")

        return "\n".join(buf)


def generate_maze(w, h, wall_density=0.15, pellet_density=0.15):
    rng = random.Random()
    all_cells = [(x, y) for y in range(h) for x in range(w)]
    k_walls = int(wall_density * len(all_cells))
    walls = set(rng.sample(all_cells, k_walls))

    start = (0, 0)
    walls.discard(start)

    free = [c for c in all_cells if c not in walls and c != start]
    k_pellets = max(1, int(pellet_density * len(free)))
    pellets = set(rng.sample(free, k_pellets))

    return walls, pellets, start
