from typing import List

import pymunk
from noise.perlin import SimplexNoise
from pygame.surface import Surface
from pymunk.body import Body
from pymunk.space import Space
from pymunk.vec2d import Vec2d

from scenes.components.rect import Rect

Y_BOTTOM = 300


class TerrainSegment:
    def __init__(self, top: Vec2d, width: int, heigth: int, space: Space):
        self.space = space
        self.width, self.height = width, heigth
        self.top_brick = self.create_top_brick(top)
        self.underlying_brick = self.create_underlying_brick(self.top_brick)

    def create_top_brick(self, center: Vec2d) -> Rect:
        r = Rect(
            int(center.x),
            int(center.y),
            self.width,
            self.height,
            self.space,
            color=(50, 50, 50),
            btype=Body.STATIC,
        )
        r.shape.friction = 1
        return r

    def create_underlying_brick(self, top: Rect) -> Rect:
        x, top_y = top.body.position
        width = self.width
        height = Y_BOTTOM - top.shape.bb.bottom
        y = top.shape.bb.bottom - height // 2
        return Rect(x, y, width, height, self.space, (100, 100, 100), btype=Body.STATIC)

    def remove_from_space(self):
        try:
            self.space.remove(
                self.top_brick.body,
                self.top_brick.shape,
                self.underlying_brick.body,
                self.underlying_brick.shape,
            )
        except AssertionError:
            pass

    def split_off(self):
        ubp = self.underlying_brick.body.position
        ubh = abs(self.underlying_brick.shape.bb.bottom - self.underlying_brick.shape.bb.top)
        new_top_coord = Vec2d(ubp.x, ubp.y + ubh // 2 - self.height // 2)
        self.top_brick = self.create_top_brick(new_top_coord)
        self.space.remove(self.underlying_brick.body, self.underlying_brick.shape)
        self.underlying_brick = self.create_underlying_brick(self.top_brick)

    def render(self, display: Surface, camera_shift: Vec2d) -> None:
        self.top_brick.render(display, camera_shift)
        self.underlying_brick.render(display, camera_shift)


class Terrain:
    def __init__(self, start: Vec2d, end: Vec2d, min_y: int, max_y: int, space: Space) -> None:
        self.min_y, self.max_y = min_y, max_y
        self.top_group = pymunk.ShapeFilter(group=9)
        self.underlying_group = pymunk.ShapeFilter(group=10)
        self.step = 5
        self.noise = SimplexNoise()
        self.space = space
        self.bricks: List[TerrainSegment] = []
        self.detached_bricks: List[Rect] = []
        for x in range(int(start.x), int(end.x), self.step):
            y = self.get_y(x)
            self.bricks.append(self.create_brick(Vec2d(x, y), self.step, self.step))

    def get_y(self, x: int) -> int:
        return self.min_y + (self.max_y - self.min_y) / 2 * self.noise.noise2(x / 1000, 0)

    def create_brick(self, center: Vec2d, width: int, height: int) -> TerrainSegment:
        r = TerrainSegment(center, width, height, self.space)
        r.top_brick.shape.filter = self.top_group
        r.underlying_brick.shape.filter = self.underlying_group
        return r

    def update(self, shift: Vec2d) -> None:
        for brick in self.detached_bricks:
            brick.lifespan -= 1
            if brick.lifespan <= 0:
                self.space.remove(brick.body, brick.shape)
                self.detached_bricks.remove(brick)

        ls = self.bricks[0]
        rs = self.bricks[-1]
        # if ls.shape.a.x < shift.x:
        #     self.segments.insert(0, self.create_segment(
        #         (ls.shape.a.x - self.seg_width, randint(self.min_y, self.max_y)),
        #         (ls.shape.a.x, ls.shape.a.y),
        #     ))

        val = shift.x + rs.top_brick.body.position.x - 2100
        if val < 0:
            ax, ay = rs.top_brick.body.position
            bx = ax + self.step
            by = self.get_y(bx)
            self.bricks.append(self.create_brick(Vec2d(bx, by), self.step, self.step))
            ls.remove_from_space()
            self.bricks.remove(ls)

    def detach_tops(self, center: Vec2d, radius: int) -> None:
        query = self.space.point_query(center, radius, self.underlying_group)
        shapes = set([s.shape for s in query])
        for s in self.bricks:
            if s.top_brick.shape not in shapes:
                continue
            s.top_brick.body.body_type = Body.DYNAMIC
            s.top_brick.color = (0, 0, 0)
            s.top_brick.body.mass = 100
            s.top_brick.lifespan = 255
            self.detached_bricks.append(s.top_brick)
            s.split_off()

    def render(self, display: Surface, camera_shift: Vec2d) -> None:
        for brick in self.bricks:
            brick.render(display, camera_shift)
        for brick in self.detached_bricks:
            brick.render(display, camera_shift)
