from ghosts.ghost_base import GhostAgent
from utils import MOVES, bfs_path

class PropGhostPatrol(GhostAgent):
    def __init__(self, name, start_pos, patrol_points):
        super().__init__(name, start_pos)
        self.patrol_points = patrol_points
        self.mode = "patrol"

    def perceive_and_update(self, env):
        los = super().perceive_and_update(env)
        saw = False
        for (x,y),typ in los.items():
            if typ == "wall": self.kb.add(f"W@{x},{y}")
            if typ == "free": self.kb.add(f"F@{x},{y}")
            if typ == "pacman":
                saw = True
                self.last_seen = (x,y)
        if saw:
            self.mode = "intercept"
        return los

    def choose_action(self, env):
        free = {(x,y) for x in range(env.w) for y in range(env.h)
                if f"W@{x},{y}" not in self.kb}

        if self.mode == "intercept" and self.last_seen:
            path = bfs_path(self.pos, self.last_seen, free)
            if path:
                nx,ny = path[0]
                dx,dy = nx-self.pos[0], ny-self.pos[1]
                for act,(mx,my) in MOVES.items():
                    if (mx,my)==(dx,dy):
                        return act

        target = self.patrol_points[self.patrol_index]
        if self.pos == target:
            self.patrol_index = (self.patrol_index+1) % len(self.patrol_points)
            target = self.patrol_points[self.patrol_index]

        path = bfs_path(self.pos, target, free)
        if path:
            nx,ny = path[0]
            dx,dy = nx-self.pos[0], ny-self.pos[1]
            for act,(mx,my) in MOVES.items():
                if (mx,my)==(dx,dy):
                    return act

        return super().choose_action(env)
