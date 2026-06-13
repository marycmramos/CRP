from ghosts.ghost_base import GhostAgent
from utils import MOVES, manhattan, bfs_path


class FOLGhostStrategic(GhostAgent):

    def perceive_and_update(self, env):
        los = super().perceive_and_update(env)

        for (x, y), typ in los.items():
            if typ == "wall":
                self.facts.add(("Wall", x, y))
            elif typ == "free":
                self.facts.add(("Free", x, y))
            elif typ == "pacman":
                self.facts.add(("At", "Pacman", x, y))
                self.last_seen = (x, y)

        return los

    def infer_future_pos(self, env):
        if not self.last_seen:
            return None

        px, py = env.pacman_pos
        self.facts.add(("At", "Pacman", px, py))

        dx = px - self.last_seen[0]
        dy = py - self.last_seen[1]

        future = (px + dx, py + dy)

        if env.in_bounds(future) and future not in env.walls:
            self.facts.add(("NextPos", "Pacman", future[0], future[1]))
            return future

        return None

    def choose_action(self, env):
        future = self.infer_future_pos(env)

        target = future if future else self.last_seen

        if target:
            free = {(x, y)
                    for x in range(env.w)
                    for y in range(env.h)
                    if not env.blocked((x, y))}

            path = bfs_path(self.pos, target, free)
            if path:
                nx, ny = path[0]
                dx, dy = nx - self.pos[0], ny - self.pos[1]

                for act, (mx, my) in MOVES.items():
                    if (mx, my) == (dx, dy):
                        return act

        if self.last_seen:
            best_action = None
            best_dist = 9999

            for act, (dx, dy) in MOVES.items():
                nxt = (self.pos[0] + dx, self.pos[1] + dy)
                if env.blocked(nxt):
                    continue

                d = manhattan(nxt, self.last_seen)
                if d < best_dist:
                    best_dist = d
                    best_action = act

            if best_action:
                return best_action
            
        if self.last_seen is None:
            preferred = ["UP", "LEFT", "RIGHT", "DOWN"]
            for act in preferred:
                dx, dy = MOVES[act]
                nxt = (self.pos[0] + dx, self.pos[1] + dy)
                if not env.blocked(nxt):
                    return act
                
        options = [
            a for a, (dx, dy) in MOVES.items()
            if not env.blocked((self.pos[0] + dx, self.pos[1] + dy))
        ]

        return options[0] if options else "UP"
