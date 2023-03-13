from abc import ABC
from logging import getLogger
from typing import Any, List

import pymunk
from pygame.event import Event
from pygame.surface import Surface

log = getLogger()


class AbstractScene(ABC):
    def __init__(self, display: Surface, fps: int) -> None:
        self.display: Surface = display
        self.size_sc: tuple = display.get_size()
        self.fps: int = fps

    def handle_event(self, event: Event) -> None:
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()


class AbstractPymunkScene(AbstractScene):
    space: pymunk.Space
    objects: List[Any]
    camera_shift: pymunk.Vec2d

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_scene()

    def handle_event(self, event: Event) -> None:
        raise NotImplementedError()

    def reset_scene(self):
        self.objects = []
        self.space = pymunk.Space()
        self.space.gravity = 0, -1000  # Set the friction coefficient of the space object
        self.space.damping = 0.5
        self.camera_shift = pymunk.Vec2d(0, 0)

    def update(self):
        self.space.step(1 / self.fps)

    def render(self):
        self.display.fill((235, 146, 52))
        for obj in self.objects:
            obj.render(self.display, self.camera_shift)
