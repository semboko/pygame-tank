from typing import List

from noise.perlin import BaseNoise, SimplexNoise
from pygame import draw
from pygame.surface import Surface
from pymunk.body import Body
from pymunk.space import Space
from pymunk.vec2d import Vec2d

from scenes.components.rect import Rect
from scenes.components.segment import Segment
from scenes.utils import convert


class Terrain:
    def __init__(self, start: Vec2d, end: Vec2d, min_y: int, max_y: int, space: Space) -> None:
        self.min_y, self.max_y = min_y, max_y
        self.step = 10
        self.noise = SimplexNoise()
        self.space = space
        self.segments: List[Segment] = []
        self.bricks: List[Rect] = []
        for x in range(int(start.x), int(end.x), self.step):
            # prev_point = start if not self.segments else self.segments[-1].shape.b
            y = self.get_y(x)
            # self.segments.append(self.create_segment(prev_point, Vec2d(x, y)))
            self.bricks.append(self.create_brick(Vec2d(x, y), self.step, self.step))

    def get_y(self, x: int) -> int:
        return self.min_y + (self.max_y - self.min_y) / 2 * self.noise.noise2(x / 1000, 0)

    def create_segment(self, a: Vec2d, b: Vec2d) -> Segment:
        s = Segment(a, b, 1, self.space, btype=Body.STATIC)
        s.shape.friction = 1
        return s

    def create_brick(self, center: Vec2d, width: int, height: int) -> Rect:
        r = Rect(int(center.x), int(center.y), width, height, self.space, btype=Body.STATIC)
        r.shape.friction = 1
        return r

    def update(self, shift: Vec2d) -> None:
        ls = self.bricks[0]
        rs = self.bricks[-1]
        # if ls.shape.a.x < shift.x:
        #     self.segments.insert(0, self.create_segment(
        #         (ls.shape.a.x - self.seg_width, randint(self.min_y, self.max_y)),
        #         (ls.shape.a.x, ls.shape.a.y),
        #     ))
        #
        val = shift.x + rs.body.position.x - 1700
        if val < 0:
            ax, ay = rs.body.position
            bx = ax + self.step
            by = self.get_y(bx)
            self.bricks.append(self.create_brick(Vec2d(bx, by), self.step, self.step))
            self.space.remove(ls.body, ls.shape)
            self.bricks.remove(ls)

    def render(self, display: Surface, camera_shift: Vec2d) -> None:
        h = display.get_height()
        for segment in self.segments:
            a = convert(segment.shape.a + camera_shift, h)
            b = convert(segment.shape.b + camera_shift, h)
            draw.line(display, (255, 255, 255), a, b, 1)

        for brick in self.bricks:
            brick.render(display, camera_shift)
