import pygame
from typing import Optional
from math import sqrt
from pymunk import Vec2d


class Explosion:
    def __init__(self, filename: str, stages: int) -> None:
        self.tile = pygame.image.load(filename)
        self.stages = stages
        self.count = 0
        self.active = False
        self.pos: Optional[pygame.Vector2] = None

    def get_area(self, stage: int) -> pygame.Rect:
        img_width, img_height = self.tile.get_size()
        row_size = sqrt(self.stages)
        sub_width, sub_height = (
            img_width // row_size,
            img_height // row_size
        )
        row = stage // row_size
        col = stage % row_size
        x, y = sub_width * col, sub_width * row
        return pygame.Rect((x, y), (sub_width, sub_height))

    def play(self, pos: pygame.Vector2) -> None:
        if self.active:
            return
        self.active = True
        self.pos = pos + pygame.Vector2(90, 0)

    def update(self):
        if self.active:
            self.count += 1

        if self.count >= self.stages:
            self.count = 0
            self.active = False
            self.pos = None

    def render(self, display: pygame.Surface, camera_shift: Vec2d) -> None:
        if not self.pos:
            return
        cropped = self.tile.subsurface(self.get_area(self.count))
        dest = cropped.get_rect(center=self.pos + camera_shift)
        display.blit(cropped, dest)
