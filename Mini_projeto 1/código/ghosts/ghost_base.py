from typing import Tuple, Optional, Set
import random
from utils import MOVES, line_of_sight

Coord = Tuple[int, int]

class GhostAgent:
    def __init__(self, name: str, start_pos: Coord):
        self.name = name
        self.pos = start_pos
        self.start_pos = start_pos

        self.kb: Set[str] = set()
        self.facts: Set[Tuple] = set()

        self.last_seen: Optional[Coord] = None
        self.mode = "idle"
        self.patrol_points = []
        self.patrol_index = 0

    def perceive_and_update(self, env):
        return line_of_sight(env, self.pos, 4)

    def choose_action(self, env):
        options = []
        for act,(dx,dy) in MOVES.items():
            nxt = (self.pos[0]+dx, self.pos[1]+dy)
            if not env.blocked(nxt):
                options.append(act)
        return random.choice(options) if options else "UP"

    def step(self, action, env):
        if action in MOVES:
            dx,dy = MOVES[action]
            nxt = (self.pos[0]+dx, self.pos[1]+dy)
            if not env.blocked(nxt):
                self.pos = nxt
