from math import degrees
from typing import List, Sequence, Tuple, Union

import pygame
import pymunk
from pygame import draw
from pygame.surface import Surface
from pymunk import Body, GearJoint, PivotJoint, Poly, RotaryLimitJoint, Shape, ShapeFilter, SimpleMotor, Space
from pymunk.vec2d import Vec2d

from scenes.components.ball import Ball
from scenes.components.bullet import Bullet
from scenes.utils import convert

TANK_WIDTH = 250
TANK_HEIGHT = 74
WHEEL_R = 9


def raw_to_poly(
    raw: Union[Tuple[Vec2d, ...], Tuple[Tuple[int, int], ...]], width: int, height: int
) -> List[Tuple[int, int]]:
    return [(int(vx - width / 2), int(height / 2 - vy)) for vx, vy in raw]


def unpack_coords(verts: Sequence[Vec2d]) -> Tuple[List[int], List[int]]:
    xs: List[int] = []
    ys: List[int] = []
    for x, y in verts:
        xs.append(int(x))
        ys.append(int(y))
    return xs, ys


def get_center(verts: Sequence[Vec2d]) -> Vec2d:
    xs, ys = unpack_coords(verts)
    return Vec2d(sum(xs) / len(xs), sum(ys) / len(ys))


def get_width(verts: Sequence[Vec2d]) -> int:
    xs, _ = unpack_coords(verts)
    return max(xs) - min(xs)


def get_height(verts: Sequence[Vec2d]) -> int:
    _, ys = unpack_coords(verts)
    return max(ys) - min(ys)


class VisualPart:
    def __init__(
        self,
        left_x: int,
        top_y: int,
        raw_verts: Tuple[Vec2d, ...],
        cf: ShapeFilter,
        image_path: str,
        space: Space,
        debug: bool = False,
    ):
        """
        :param left_x: Global leftmost x-coordinate of the shape
        :param top_y: Global topmost y-coordinate of the shape
        :param raw_verts: Figma-based relative coordinates of the shape
        :param cf: Collision filter for the shape
        :param space: Space to which the shape will be placed after creating
        """
        self.collision_filter = cf
        self.space = space

        self.width, self.height = self.get_obj_dimensions(raw_verts)

        self.body = self.generate_body(left_x, top_y)
        self.shape = self.generate_shape(raw_verts, cf)

        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()

        self.debug = debug

    def get_obj_dimensions(self, raw_verts: Tuple[Vec2d, ...]):
        return get_width(raw_verts), get_height(raw_verts)

    def generate_body(self, left_x: int, top_y: int) -> Body:
        cx, cy = left_x + self.width / 2, top_y - self.height / 2
        body = Body()
        body.position = cx, cy
        self.space.add(body)
        return body

    def generate_shape(self, raw_verts: Tuple[Vec2d, ...], cf: ShapeFilter) -> Shape:
        shape = Poly(self.body, vertices=raw_to_poly(raw_verts, self.width, self.height))
        shape.density = 1
        shape.filter = cf
        self.space.add(shape)
        return shape

    def debug_draw(self, display: Surface):
        h = display.get_height()
        # Draw the shape
        verts = [convert(self.body.local_to_world(v), h) for v in self.shape.get_vertices()]
        draw.polygon(display, (255, 255, 0), verts, 1)
        # Draw the center of mass
        draw.circle(display, (255, 255, 0), convert(self.body.position, h), 2, 1)

    def render(self, display: Surface):
        h = display.get_height()
        last_rect = self.image.get_rect()
        rotated_image = pygame.transform.rotate(self.image, degrees(self.body.angle))
        new_rect = rotated_image.get_rect(center=convert(self.body.position, h))
        display.blit(rotated_image, new_rect)

        if self.debug:
            self.debug_draw(display)


class TankBase(VisualPart):
    def __init__(self, left_x: int, top_y: int, cf: ShapeFilter, space: Space, debug: bool = False):
        raw_vertices = (
            Vec2d(0, 0),
            Vec2d(0, 20),
            Vec2d(10, 20),
            Vec2d(37, 33),
            Vec2d(172, 33),
            Vec2d(200, 28),
            Vec2d(204, 10),
            Vec2d(73, 6),
            Vec2d(48, 0),
            Vec2d(0, 0),
        )

        super().__init__(left_x, top_y, raw_vertices, cf, "./scenes/assets/body.png", space, debug)


class TankWheel(VisualPart):
    def __init__(self, global_x: int, global_y: int, cf: ShapeFilter, space: Space, debug: bool = False) -> None:
        super().__init__(global_x, global_y, tuple(), cf, "./scenes/assets/wheel.png", space, debug)

    def get_obj_dimensions(self, raw_verts: Tuple[Vec2d, ...]):
        return 2 * WHEEL_R, 2 * WHEEL_R

    def generate_shape(self, _: Tuple[Vec2d, ...], cf: ShapeFilter) -> Shape:
        shape = pymunk.Circle(self.body, WHEEL_R)
        shape.density = 1
        shape.friction = 1
        shape.filter = cf
        self.space.add(shape)
        return shape

    def attach_to(self, tank_base: Body) -> pymunk.PivotJoint:
        wlocal_x, wlocal_y = tank_base.world_to_local(self.body.position)
        wheel_attachment = PivotJoint(tank_base, self.body, (wlocal_x, wlocal_y), (0, 0))
        self.space.add(wheel_attachment)
        return wheel_attachment

    def debug_draw(self, display: Surface):
        pass


class MotorWheel(TankWheel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = pygame.image.load("./scenes/assets/motor_wheel.png")


class Turret(VisualPart):
    def __init__(self, left_x: int, top_y: int, cf: ShapeFilter, space: Space, debug: bool = False):
        raw_verts = (
            Vec2d(0, 16),
            Vec2d(2, 25),
            Vec2d(16, 26),
            Vec2d(38, 30),
            Vec2d(43, 36),
            Vec2d(117, 36),
            Vec2d(132, 27),
            Vec2d(124, 20),
            Vec2d(66, 14),
            Vec2d(91, 0),
            Vec2d(71, 0),
            Vec2d(47, 15),
        )
        super().__init__(left_x, top_y, raw_verts, cf, "./scenes/assets/turret.png", space, debug)

    def attach_to(self, tank_base: Body):
        bb = self.shape.bb
        lb_x, lb_y = bb.left, bb.bottom
        rb_x, rb_y = bb.right, bb.bottom
        pj1 = PivotJoint(
            tank_base, self.body, tank_base.world_to_local((lb_x, lb_y)), self.body.world_to_local((lb_x, lb_y))
        )
        pj2 = PivotJoint(
            tank_base, self.body, tank_base.world_to_local((rb_x, rb_y)), self.body.world_to_local((rb_x, rb_y))
        )
        self.space.add(pj1, pj2)


class TankGun(VisualPart):
    def __init__(self, left_x: int, top_y: int, cf: ShapeFilter, space: Space, debug: bool = False):
        raw_verts = (
            Vec2d(0, 0),
            Vec2d(0, 8),
            Vec2d(94, 8),
            Vec2d(94, 4),
            Vec2d(90, 2),
            Vec2d(90, 4),
            Vec2d(49, 3),
            Vec2d(45, 0),
            Vec2d(35, 0),
            Vec2d(33, 3),
            Vec2d(25, 2),
            Vec2d(13, 2),
        )
        super().__init__(left_x, top_y, raw_verts, cf, "./scenes/assets/gun.png", space, debug)

    def attach_to(self, turret: Turret):
        tr, tt = turret.shape.bb.right, turret.shape.bb.top
        gl, gt = self.shape.bb.left, self.shape.bb.top
        attachment = PivotJoint(
            turret.body,
            self.body,
            turret.body.world_to_local((tr - 20, tt - turret.height / 2 - 10)),
            self.body.world_to_local((gl, gt - self.height / 2)),
        )
        self.space.add(attachment)


class TankSoundEffects:
    def __init__(self):
        self.engine_1 = pygame.mixer.Sound("./scenes/assets/engine1.mp3")
        self.engine_2 = pygame.mixer.Sound("./scenes/assets/engine2.mp3")
        self.engine_3 = pygame.mixer.Sound("./scenes/assets/engine3.mp3")
        self.shot = pygame.mixer.Sound("./scenes/assets/fire_001.mp3")
        self.explosion = pygame.mixer.Sound("./scenes/assets/DeathFlash.flac")

        self._current_speed = 0
        self._last_diff = 0
        self.engine_sound = self.engine_1

    def update(self, speed: float = 0):
        diff = abs(int(self._current_speed - speed))
        # if diff > 1:
        #     diff = 1
        #
        # if self._last_diff != diff:
        #     self.engine_sound.stop()
        #     if diff == 1:
        #         self.engine_sound = self.engine_2
        #     if diff == 0:
        #         self.engine_sound = self.engine_1
        #     self.engine_sound.play(0)
        #
        # self._current_speed = speed
        # self._last_diff = diff
        #
        # if not pygame.mixer.get_busy():
        #     self.engine_sound.play(0)


class Tank:
    tank_base: TankBase
    collision_filter: ShapeFilter
    wheels: Sequence[TankWheel]
    motor: SimpleMotor
    turret_shape: Shape

    def __init__(self, x, y, space: Space, debug: bool = False):
        self.collision_filter = ShapeFilter(group=0b1)
        self.space = space
        self.debug = debug

        self.top_y = y + TANK_HEIGHT / 2
        self.left_x = x - TANK_WIDTH / 2

        self.tank_base = TankBase(self.left_x, self.top_y - 30, self.collision_filter, space, debug)
        self.wheels = self.get_wheels()
        self.motor_wheel = self.get_motor_wheel()
        self.motor = self.get_motor()
        self.turret = self.get_turret()
        self.gun = self.get_gun()
        self.bullet, self.bullet_holder = self.get_bullet()

        self.sound_effects = TankSoundEffects()

    def get_wheels(self) -> Sequence[TankWheel]:
        wheel_xs = (38, 57, 76, 95, 115, 135, 160)
        wheel_y = self.top_y - 55
        wheels = []
        for wheel_x in wheel_xs:
            wheel_x = self.left_x + wheel_x
            new_wheel = TankWheel(wheel_x, wheel_y, self.collision_filter, self.space)
            new_wheel.attach_to(self.tank_base.body)
            wheels.append(new_wheel)
        front_wheel = TankWheel(self.left_x + 184, self.top_y - 50, self.collision_filter, self.space)
        front_wheel.attach_to(self.tank_base.body)
        wheels.append(front_wheel)
        return wheels

    def get_motor_wheel(self) -> MotorWheel:
        mw = MotorWheel(self.left_x + 14, self.top_y - 41, self.collision_filter, self.space)
        mw.attach_to(self.tank_base.body)
        return mw

    def get_motor(self) -> SimpleMotor:
        motor = SimpleMotor(self.tank_base.body, self.motor_wheel.body, 0)
        self.space.add(motor)
        for wheel in self.wheels:
            gear = GearJoint(self.motor_wheel.body, wheel.body, 0, 1)
            self.space.add(gear)
        return motor

    def get_turret(self) -> Turret:
        turret = Turret(self.left_x + 36, self.top_y + 5, self.collision_filter, self.space, self.debug)
        turret.attach_to(self.tank_base.body)
        return turret

    def get_gun(self) -> TankGun:
        gun = TankGun(self.left_x + 155, self.top_y - 22, self.collision_filter, self.space, self.debug)
        self.gun_joint = RotaryLimitJoint(self.turret.body, gun.body, min=0, max=0.1)
        self.space.add(self.gun_joint)
        gun.attach_to(self.turret)
        return gun

    def get_bullet(self) -> Tuple[Bullet, PivotJoint]:
        x, y = self.gun.shape.bb.right, self.gun.shape.bb.top
        bullet = Bullet(x, y, 5, self.space)
        bullet.shape.elasticity = 0.1
        bullet.body.mass = 400
        bullet.shape.filter = self.collision_filter
        bullet_holder = PivotJoint(self.gun.body, bullet.body, self.gun.body.world_to_local((x, y)), (0, 0))
        self.space.add(bullet_holder)
        return bullet, bullet_holder

    def shot(self) -> Ball:
        self.sound_effects.shot.play()
        try:
            self.space.remove(self.bullet_holder)
        except AssertionError:
            pass
        force = self.bullet.start(self.gun.body.angle)
        self.tank_base.body.apply_force_at_local_point((-force[0] * 4, -force[1] * 4), (0, 0))
        prev_bullet = self.bullet

        self.bullet, self.bullet_holder = self.get_bullet()
        return prev_bullet

    def update_velocity(self, keys: Sequence[bool]):
        if keys[pygame.K_d]:
            self.motor.rate += 1
            return
        if keys[pygame.K_a]:
            self.motor.rate -= 1
            return

        self.motor.rate *= 0.8

    def update_gun_angle(self, keys: Sequence[bool]):
        relative_angle = self.gun.body.angle - self.turret.body.angle
        if keys[pygame.K_UP] and relative_angle > 0:
            self.gun_joint.min -= 0.01
            self.gun_joint.max -= 0.01
        if keys[pygame.K_DOWN] and relative_angle < 1:
            self.gun_joint.min += 0.01
            self.gun_joint.max += 0.01

    def update(self):
        keys = pygame.key.get_pressed()
        self.update_velocity(keys)
        self.update_gun_angle(keys)
        self.sound_effects.update(speed=self.motor.rate)

    def render(self, display: Surface):
        draw.circle(
            display,
            (255, 255, 0),
            convert((self.left_x + TANK_WIDTH // 2, self.top_y - TANK_HEIGHT // 2), display.get_height()),
            5,
            1,
        )
        for wheel in self.wheels:
            wheel.render(display)
        self.motor_wheel.render(display)
        self.tank_base.render(display)
        self.gun.render(display)
        self.bullet.render(display)
        self.turret.render(display)
