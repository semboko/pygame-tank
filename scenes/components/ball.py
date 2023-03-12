from math import cos, sin
from typing import Tuple

import pygame
import pymunk
from pygame.surface import Surface

from scenes.utils import convert


class Ball:
    def __init__(
        self,
        x: int,
        y: int,
        r: int,
        space: pymunk.Space,
        btype: int = pymunk.Body.DYNAMIC,
        color: Tuple[int, int, int] = (244, 0, 0),
    ):
        self.body = pymunk.Body(body_type=btype)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, r)
        self.shape.density = 0.1
        self.shape.elasticity = 0.9
        self.shape.friction = 0.7
        self.r = r
        self.color = color
        space.add(self.body, self.shape)

    def render(self, display: Surface) -> None:
        h = display.get_height()
        pygame.draw.circle(display, self.color, convert(self.body.position, h), self.r)
        alpha = self.body.angle
        line_end = cos(alpha) * self.r, sin(alpha) * self.r
        pygame.draw.line(
            display, (0, 0, 0), convert(self.body.position, h), convert(self.body.local_to_world(line_end), h), 1
        )
