from typing import Tuple

import pygame
import pymunk
from pygame.surface import Surface

from scenes.utils import convert


class Segment:
    def __init__(
        self, a: Tuple[int, int], b: Tuple[int, int], r: int, space: pymunk.Space, btype: int = pymunk.Body.DYNAMIC
    ):
        self.body = pymunk.Body(body_type=btype)
        self.shape = pymunk.Segment(self.body, a, b, r)
        self.shape.elasticity = 0.9
        self.shape.density = 1
        self.shape.mass = 2
        self.shape.friction = 0.7
        self.r = r
        space.add(self.body, self.shape)

        # Create a new pygame.Rect object for the segment
        min_x = min(a[0], b[0]) - r
        max_x = max(a[0], b[0]) + r
        min_y = min(a[1], b[1]) - r
        max_y = max(a[1], b[1]) + r
        self.rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def render(self, display: Surface) -> None:
        h = display.get_height()
        a = convert(self.shape.a, h)
        b = convert(self.shape.b, h)
        pygame.draw.line(display, (0, 0, 0), a, b, 10)
