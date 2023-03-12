import pymunk
from pygame import draw
from pygame.surface import Surface

from scenes.components import Ball
from scenes.components.pj import PJ
from scenes.utils import convert


class CarBody:
    rear_sleeve: Ball
    rear_joint: PJ
    rear_suspension: PJ
    rear_wheel: Ball

    def __init__(self, x, y, width, height, space: pymunk.Space):
        self.r = min(width, height) // 2
        self.space = space
        self.body = pymunk.Body()
        self.body.position = x + width / 2, y + height / 2

        vertices = (
            (-width // 2, -height // 2),
            (+width // 2, -height // 2),
            (+width // 2, +height // 2),
            (-width // 2, +height // 2),
        )

        self.shape = pymunk.Poly(self.body, vertices=vertices)
        self.shape.density = 0.5
        self.collision_filter = pymunk.ShapeFilter(group=0b1)
        self.shape.filter = self.collision_filter

        space.add(self.body, self.shape)

        self.width = width
        self.height = height

        self.add_rear_suspension(-width * 0.75, -height * 0.7)
        self.add_front_suspension(width * 0.75, -height * 0.7)
        frame = pymunk.PinJoint(self.rear_sleeve.body, self.front_sleeve.body, (0, 0), (0, 0))
        self.space.add(frame)
        self.frame_obj = PJ(frame)

        self.front_wheel.shape.filter = self.collision_filter
        self.rear_wheel.shape.filter = self.collision_filter
        self.front_sleeve.shape.filter = self.collision_filter
        self.rear_sleeve.shape.filter = self.collision_filter

        self.motor = pymunk.SimpleMotor(self.rear_wheel.body, self.body, 0)
        self.space.add(self.motor)
        self.space.add(pymunk.GearJoint(self.front_wheel.body, self.rear_wheel.body, 0, 1))

    def add_rear_suspension(self, wheel_x: int, wheel_y: int):
        gwheel_x, gwheel_y = self.body.local_to_world((wheel_x, wheel_y))
        self.rear_sleeve = Ball(int(gwheel_x), int(gwheel_y), 5, self.space)
        joint = pymunk.PinJoint(self.body, self.rear_sleeve.body, (-self.width // 2, -self.height // 2), (0, 0))
        suspension = pymunk.PinJoint(self.body, self.rear_sleeve.body, (self.width // 2, 0), (0, 0))
        self.rear_joint = PJ(joint)
        self.rear_suspension = PJ(suspension, color=(0, 0, 0))
        self.space.add(joint)
        self.space.add(suspension)

        self.rear_wheel = Ball(int(gwheel_x), int(gwheel_y), 30, self.space)
        self.rear_wheel.shape.density = 0.2
        self.rear_wheel.shape.friction = 1

        attachment = pymunk.PivotJoint(self.rear_sleeve.body, self.rear_wheel.body, (0, 0), (0, 0))
        attachment.collide_bodies = False
        self.space.add(attachment)

    def add_front_suspension(self, wheel_x: int, wheel_y: int):
        gwheel_x, gwheel_y = self.body.local_to_world((wheel_x, wheel_y))
        self.front_sleeve = Ball(int(gwheel_x), int(gwheel_y), 5, self.space)

        joint = pymunk.PinJoint(self.body, self.front_sleeve.body, (self.width // 2, -self.height // 2), (0, 0))
        self.space.add(joint)
        self.front_joint = PJ(joint)

        suspension = pymunk.PinJoint(self.body, self.front_sleeve.body, (-self.width // 2, 0), (0, 0))
        self.space.add(suspension)
        self.front_suspension = PJ(suspension, color=(0, 0, 0))

        self.front_wheel = Ball(int(gwheel_x), int(gwheel_y), 30, self.space)
        self.front_wheel.shape.density = 0.2
        self.front_wheel.shape.friction = 1

        attachment = pymunk.PivotJoint(self.front_sleeve.body, self.front_wheel.body, (0, 0), (0, 0))
        attachment.collide_bodies = False
        self.space.add(attachment)

    def render(self, display: Surface):
        h = display.get_height()
        vert = [convert(self.body.local_to_world(v), h) for v in self.shape.get_vertices()]
        draw.polygon(display, (52, 122, 235), vert)
        cx, cy = convert(self.body.local_to_world(self.body.center_of_gravity), h)
        draw.circle(display, (161, 190, 237), (cx, cy), self.r, 1)

        self.rear_wheel.render(display)
        self.rear_sleeve.render(display)
        self.rear_joint.render(display)
        self.rear_suspension.render(display)

        self.front_wheel.render(display)
        self.front_sleeve.render(display)
        self.front_joint.render(display)
        self.front_suspension.render(display)

        self.frame_obj.render(display)
