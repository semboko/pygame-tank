from typing import Tuple

import pygame
import pymunk
from pymunk import DampedSpring, PinJoint, PivotJoint

from scenes.utils import convert


class PJ:
    def __init__(self, joint: pymunk.Constraint, color: Tuple[int, int, int] = (255, 255, 0)) -> None:
        self.joint = joint
        self.color = color

    def render(self, display: pygame.surface.Surface) -> None:
        h = display.get_height()
        if isinstance(self.joint, (PivotJoint, PinJoint, DampedSpring)):
            anchor_a = self.joint.a.local_to_world(self.joint.anchor_a)
            anchor_b = self.joint.b.local_to_world(self.joint.anchor_b)
        else:
            anchor_a = self.joint.a.position
            anchor_b = self.joint.b.position
        x1 = convert(anchor_a, h)
        x2 = convert(anchor_b, h)
        pygame.draw.line(display, self.color, x1, x2, 3)
