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
from scenes.utils import convert, get_height, get_width, raw_to_poly


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

    def get_render_position(self, camera_shift: pymunk.Vec2d = pymunk.Vec2d(0, 0)) -> pymunk.Vec2d:
        return self.body.position + camera_shift

    def render(self, display: Surface, camera_shift: pymunk.Vec2d):
        h = display.get_height()
        rotated_image = pygame.transform.rotate(self.image, degrees(self.body.angle))
        new_rect = rotated_image.get_rect(center=convert(self.get_render_position(camera_shift), h))
        display.blit(rotated_image, new_rect)

        if self.debug:
            self.debug_draw(display)
