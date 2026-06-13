import os
import sys
import select
import collections
from typing import Tuple, Set, Dict, List, Optional

Coord = Tuple[int, int]

def get_pressed_key() -> Optional[str]:
    if os.name == 'nt':
        try:
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in [b'\x00', b'\xe0']:
                    ch2 = msvcrt.getch()
                    if ch2 == b'H': return 'UP'
                    if ch2 == b'P': return 'DOWN'
                    if ch2 == b'M': return 'RIGHT'
                    if ch2 == b'K': return 'LEFT'
                elif ch.decode('utf-8', errors='ignore').lower() == 'q':
                    return 'QUIT'
            return None
        except ImportError:
            return None
    else:
        try:
            import termios, tty
            tty.setcbreak(sys.stdin.fileno(), termios.TCSANOW)

            if not select.select([sys.stdin], [], [], 0)[0]:
                return None

            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A': return 'UP'
                    if ch3 == 'B': return 'DOWN'
                    if ch3 == 'C': return 'RIGHT'
                    if ch3 == 'D': return 'LEFT'
            elif ch.lower() == 'q':
                return 'QUIT'
            return None
        except:
            return None


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


MOVES = {
    'RIGHT': (1, 0),
    'LEFT': (-1, 0),
    'DOWN': (0, 1),
    'UP': (0, -1),
}


def line_of_sight(env, gpos: Coord, max_dist: int = 4) -> Dict[Coord, str]:
    percepts = {}
    gx, gy = gpos

    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        for d in range(1, max_dist + 1):
            x, y = gx + dx*d, gy + dy*d
            if not env.in_bounds((x, y)):
                break

            if (x, y) in env.walls:
                percepts[(x, y)] = "wall"
                break

            if (x, y) == env.pacman_pos:
                percepts[(x, y)] = "pacman"
            elif (x, y) in env.pellets:
                percepts[(x, y)] = "pellet"
            else:
                percepts[(x, y)] = "free"

    return percepts


def bfs_path(start: Coord, goal: Coord, free: Set[Coord]) -> Optional[List[Coord]]:
    if start == goal:
        return []

    q = collections.deque([start])
    parent = {start: None}

    while q:
        cur = q.popleft()
        for dx, dy in MOVES.values():
            nxt = (cur[0] + dx, cur[1] + dy)

            if nxt not in free:
                continue
            if nxt in parent:
                continue

            parent[nxt] = cur

            if nxt == goal:
                path = []
                node = nxt
                while parent[node] is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path

            q.append(nxt)

    return None
