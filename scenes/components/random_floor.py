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
        self.space = space
        self.points: List[Tuple[int, int]] = []
        total_width = end_x - start_x
        self.seg_width = total_width / segments
        self.points.append((int(start_x), int((min_y + max_y) / 2)))
        for seg in range(segments):
            last_x, last_y = self.points[-1]
            next_x = int(last_x + self.seg_width)
            next_y = randint(int(min_y), int(max_y))
            self.points.append((next_x, next_y))

        self.segments = [self.create_segment(p1, p2) for p1, p2 in pairwise(self.points)]

        self.start_x = start_x
        self.end_x = end_x
        self.min_y, self.max_y = int(min_y), int(max_y)

    def create_segment(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> Segment:
        s = Segment(p1, p2, 2, self.space, btype=pymunk.Body.STATIC)
        s.shape.friction = 1
        return s

    def update(self, shift: pymunk.Vec2d) -> None:
        ls = self.segments[0]
        rs = self.segments[-1]
        if ls.shape.a.x < shift.x:
            self.segments.insert(0, self.create_segment(
                (ls.shape.a.x - self.seg_width, randint(self.min_y, self.max_y)),
                (ls.shape.a.x, ls.shape.a.y),
            ))

        val = shift.x + rs.shape.b.x - 1700
        if val < 0:
            self.segments.append(self.create_segment(
                (rs.shape.b.x, rs.shape.b.y),
                (rs.shape.b.x + self.seg_width, randint(self.min_y, self.max_y))
            ))

    def render(self, display: Surface, camera_shift: pymunk.Vec2d) -> None:
        h = display.get_height()
        for segment in self.segments:
            a = convert(segment.shape.a + camera_shift, h)
            b = convert(segment.shape.b + camera_shift, h)
            draw.line(display, (255, 255, 255), a, b, 1)
