from typing import Sequence

import pygame
from pygame.event import Event

from scenes.abstract import AbstractPymunkScene
from scenes.components.ball import Ball
from scenes.components.car import CarBody
from scenes.components.random_floor import RandomFloor
from scenes.utils import convert


class CarScene(AbstractPymunkScene):
    def reset_scene(self):
        super().reset_scene()
        self.cb = CarBody(288, 150, 100, 50, self.space)
        floor = RandomFloor(0, self.display.get_width(), 0, 100, 30, self.space)
        self.objects.extend((floor, self.cb))

    def update_center_of_gravity(self, pressed_keys: Sequence[bool]):
        gx, gy = self.cb.body.center_of_gravity

        if pressed_keys[pygame.K_RIGHT] and gx <= 20:
            self.cb.body.center_of_gravity = (gx + 5, gy)
            return

        if pressed_keys[pygame.K_LEFT] and gx >= -20:
            self.cb.body.center_of_gravity = (gx - 5, gy)
            return

        self.cb.body.center_of_gravity = (round(gx * 0.9, 1), gy)

    def update_motor_rate(self, pressed_keys: Sequence[bool]):
        if pressed_keys[pygame.K_a]:
            self.cb.motor.rate += 1
            return
        if pressed_keys[pygame.K_d]:
            self.cb.motor.rate -= 1
            return

        self.cb.motor.rate *= 0.8

    def update(self):
        super().update()
        keys = pygame.key.get_pressed()
        self.update_center_of_gravity(keys)
        self.update_motor_rate(keys)

        if self.cb.body.position[1] < 0:
            self.reset_scene()

        for obj in self.objects:
            if isinstance(obj, Ball):
                x, y = obj.body.position
                if y < 0:
                    self.objects.remove(obj)

    def handle_event(self, event: Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_scene()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.dict["pos"]
            if len(self.objects) <= 200:
                ball = Ball(*convert((x, y), self.display.get_height()), 5, self.space)
                self.objects.append(ball)
