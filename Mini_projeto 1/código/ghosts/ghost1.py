from ghosts.ghost_base import GhostAgent
from utils import MOVES, bfs_path

class PropGhostChaser(GhostAgent):
    def perceive_and_update(self, env):
        los = super().perceive_and_update(env)
        for (x,y),typ in los.items():
            if typ == "wall":  self.kb.add(f"W@{x},{y}")
            if typ == "free":  self.kb.add(f"F@{x},{y}")
            if typ == "pacman":
                self.kb.add(f"P@{x},{y}")
                self.last_seen = (x,y)
                self.mode = "chase"
        if self.last_seen is None:
            self.mode = "seek"
        return los

    def choose_action(self, env):
        if self.mode == "chase" and self.last_seen:
            free = {(x,y) for x in range(env.w) for y in range(env.h)
                    if f"W@{x},{y}" not in self.kb}
            path = bfs_path(self.pos, self.last_seen, free)
            if path:
                nx,ny = path[0]
                dx,dy = nx-self.pos[0], ny-self.pos[1]
                for act,(mx,my) in MOVES.items():
                    if (mx,my)==(dx,dy):
                        return act
        return super().choose_action(env)
