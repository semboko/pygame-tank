from random import random

import pygame
from pygame.event import Event
from pymunk import Vec2d

from scenes.abstract import AbstractPymunkScene
from scenes.components.ball import Ball
from scenes.components.bullet import Bullet
from scenes.components.random_floor import RandomFloor
from scenes.components.rect import Rect
from scenes.components.tank import Tank
from scenes.utils import convert


class TankScene(AbstractPymunkScene):
    tank: Tank
    floor: RandomFloor

    def reset_scene(self):
        super().reset_scene()
        pygame.mixer.stop()
        self.tank = Tank(250, 460, self.space, debug=False)
        self.floor = RandomFloor(0, self.display.get_width(), 0, 80, 20, self.space)
        self.objects.extend((self.tank, self.floor))

    def update(self):
        super().update()
        self.camera_shift = self.tank.get_camera_shift()
        self.floor.update(self.camera_shift)
        self.tank.update()
        self.update_bullets()
        self.update_balls()

    def update_bullets(self):
        for obj in self.objects:
            if not isinstance(obj, Bullet):
                continue
            if obj.is_outside(self.display):
                obj.remove(self.space)
                self.objects.remove(obj)
                continue
            if obj.ready_to_explode(self.space):
                self.tank.sound_effects.explosion.play()
                obj.explode(self.space)
                self.objects.remove(obj)

    def update_balls(self):
        for obj in self.objects:
            if type(obj) in (
                Ball,
                Rect,
                Bullet,
            ):
                if obj.body.position.y < 0:
                    self.space.remove(obj.body, obj.shape)
                    self.objects.remove(obj)
                    print(f"Obj {type(obj)} is removed")

    def handle_event(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_scene()

            if event.key == pygame.K_SPACE:
                bullet = self.tank.shot()
                self.objects.append(bullet)

        if event.type == pygame.MOUSEBUTTONDOWN:
            h = self.display.get_height()
            pos = Vec2d(*event.pos) - self.camera_shift
            obj = Ball(*convert(pos, h), 10, self.space, color=(55, 252, 10))
            obj.shape.friction = 1
            obj.shape.density = 0.1
            obj.body.angle = 3.14 * random()
            self.objects.append(obj)
