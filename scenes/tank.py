from random import random

import pygame
from pygame.event import Event
from pygame.surface import Surface
from pymunk import Vec2d

from scenes.abstract import AbstractPymunkScene
from scenes.components.ball import Ball
from scenes.components.bullet import Bullet
from scenes.components.rect import Rect
from scenes.components.tank import Tank
from scenes.components.terrain import Terrain
from scenes.utils import convert


class Duck(Ball):
    image = pygame.image.load("./scenes/assets/rubber_duck.png")

    def render(self, display: Surface, camera_shift: Vec2d = Vec2d(0, 0)) -> None:
        s = pygame.transform.rotate(self.image, self.body.angle)
        dest = s.get_rect(center=convert(self.body.position, display.get_height()) + camera_shift)
        display.blit(s, dest)


class TankScene(AbstractPymunkScene):
    tank: Tank
    floor: Terrain

    def reset_scene(self):
        super().reset_scene()
        pygame.mixer.stop()
        self.tank = Tank(250, 360, self.space, debug=False)
        self.floor = Terrain(Vec2d(0, 0), Vec2d(self.display.get_width(), 0), 100, 300, self.space)
        self.objects.extend((self.tank, self.floor))

    def update(self):
        super().update()
        self.camera_shift = self.tank.get_camera_shift()
        self.floor.update(self.camera_shift)
        self.tank.update()
        self.update_bullets()
        self.update_balls()

        self.handle_pressed(pygame.key.get_pressed())

    def update_bullets(self):
        for obj in self.objects:
            if not isinstance(obj, Bullet):
                continue
            bullet = obj
            if bullet.is_outside(self.display):
                bullet.remove(self.space)
                self.objects.remove(bullet)
                continue
            if bullet.ready_to_explode(self.space):
                self.tank.sound_effects.explosion.play()
                self.floor.detach_tops(bullet.body.position, 30)
                bullet.explode(self.space)
                self.objects.remove(bullet)

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

    def handle_pressed(self, keys) -> None:
        pass

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
            obj = Duck(*convert(pos, h), 15, self.space, color=(55, 252, 10))
            obj.body.mass = 50000
            obj.shape.friction = 1
            obj.shape.density = 0.1
            obj.body.angle = 3.14 * random()
            self.objects.append(obj)
