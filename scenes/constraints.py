import pygame
import pymunk
from pygame.event import Event
from pymunk.constraints import GearJoint, PivotJoint, SimpleMotor

from scenes.abstract import AbstractPymunkScene
from scenes.components import Ball, Segment
from scenes.utils import convert


class ConstraintScene(AbstractPymunkScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ball1 = Ball(250, 250, 30, self.space)
        ball2 = Ball(350, 250, 30, self.space)

        self.space.add(PivotJoint(ball1.body, self.space.static_body, (250, 250)))
        # spring = PinJoint(ball1.body, ball2.body, (0, -30), (-30, 0))
        # self.space.add(spring)

        self.space.add(SimpleMotor(ball1.body, self.space.static_body, 3.14))
        self.space.add(GearJoint(ball1.body, ball2.body, 0, 0.5))

        floor = Segment((0, 20), (500, 20), 5, self.space, btype=pymunk.Body.STATIC)

        self.objects.extend((ball1, ball2, floor))

    def handle_event(self, event: Event) -> None:
        h = self.display.get_height()

        if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 5:
            x, y = convert(event.dict["pos"], h)
            self.objects.append(Ball(x, y, 2, self.space))
        if event.type == pygame.MOUSEBUTTONDOWN and event.dict["button"] == 3:
            x, y = convert(event.dict["pos"], h)
            objs = self.space.point_query((x, y), 2, pymunk.ShapeFilter())
            if objs and objs[0].shape:
                body = objs[0].shape.body
                body.apply_impulse_at_local_point((0, -20000), (20, 0))
