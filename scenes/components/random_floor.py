from itertools import pairwise
from random import randint
from typing import List, Tuple

import pymunk
from pygame import draw
from pygame.surface import Surface

from scenes.components.segment import Segment
from scenes.utils import convert


class RandomFloor:
    def __init__(self, start_x: float, end_x: float, min_y: float, max_y: float, segments: int, space: pymunk.Space):
        self.points: List[Tuple[int, int]] = []
        total_width = end_x - start_x
        seg_width = total_width / segments
        self.points.append((int(start_x), int((min_y + max_y) / 2)))
        for seg in range(segments):
            last_x, last_y = self.points[-1]
            next_x = int(last_x + seg_width)
            next_y = randint(int(min_y), int(max_y))
            self.points.append((next_x, next_y))

        self.segments = []
        for p1, p2 in pairwise(self.points):
            s = Segment(p1, p2, 2, space, btype=pymunk.Body.STATIC)
            s.shape.friction = 1
            self.segments.append(s)

        self.start_x = start_x
        self.end_x = end_x

    def render(self, display: Surface):
        h = display.get_height()
        verts = [convert(s, h) for s in self.points]
        verts = [convert((int(self.start_x), 0), h)] + verts + [convert((int(self.end_x), 0), h)]
        draw.polygon(display, (0, 0, 0), verts)
