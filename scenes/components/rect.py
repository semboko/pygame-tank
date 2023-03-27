from typing import Tuple

import pygame
import pymunk
from pygame.surface import Surface

from scenes.utils import convert
from math import inf


class Rect:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        space: pymunk.Space,
        color: Tuple[int, int, int] = (255, 0, 0),
        btype: int = pymunk.Body.DYNAMIC,
        lifespan: float = inf,
    ) -> None:
        self.space = space
        self.color = color
        self.body = pymunk.Body(body_type=btype)
        self.body.position = x, y
        verts = (
            (-width // 2, -height // 2),
            (width // 2, -height // 2),
            (width // 2, height // 2),
            (-width // 2, height // 2),
        )
        self.shape = pymunk.Poly(self.body, verts)
        self.shape.density = 1
        self.lifespan = lifespan
        space.add(self.body, self.shape)

    def update(self):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.space.remove(self.body, self.shape)

    def render(self, display: Surface, camera_shift: pymunk.Vec2d = pymunk.Vec2d(0, 0)) -> None:
        h = display.get_height()
        verts = [convert(self.body.local_to_world(v) + camera_shift, h) for v in self.shape.get_vertices()]
        pygame.draw.polygon(display, self.color, verts)
