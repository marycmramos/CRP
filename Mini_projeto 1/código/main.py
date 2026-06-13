import time
from utils import get_pressed_key, MOVES
from environment import Environment, generate_maze

from ghosts.ghost1 import PropGhostChaser
from ghosts.ghost2 import PropGhostPatrol
from ghosts.ghost3 import FOLGhostStrategic


def run_game(env: Environment, max_steps: int = 400, sleep_s: float = 0.7):
    for _ in range(max_steps):
        if env.finished or env.over:
            break

        key = get_pressed_key()
        action = key if key else "WAIT"

        if action == "QUIT":
            break

        if action in MOVES:
            env.step(action, move_ghosts=True)
        else:
            env.step(action, move_ghosts=False)

        print(env.render())
        print()
        time.sleep(sleep_s)


def run_pacman():
    w, h = 20, 20
    walls, pellets, start = generate_maze(w, h)
    env = Environment(w, h, walls, pellets, start)

    g1 = PropGhostChaser("Chaser", (w-1, 0))
    g2 = PropGhostPatrol("Patrol", (0, h-1), patrol_points=[(3,3), (15,3), (15,15), (3,15)])
    g3 = FOLGhostStrategic("Strategic", (w-1, h-1))

    env.ghosts = [g1, g2, g3]

    run_game(env)


if __name__ == "__main__":
    run_pacman()
