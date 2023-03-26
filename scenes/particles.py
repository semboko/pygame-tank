from typing import List, Tuple

from pygame.event import Event
from pygame.surface import Surface
from pymunk import Body, Shape, Space, Vec2d

from scenes.abstract import AbstractPymunkScene
from scenes.components.ball import Ball
from scenes.components.random_floor import RandomFloor

RGB = Tuple[int, int, int]


class Particle(Ball):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lifetime = 512
        self.body.apply_force_at_world_point((0, 50000), (0, 0))

    @property
    def is_alive(self):
        return self.lifetime >= 0


class ParticlePool:

    particles: List[Particle]

    def __init__(self, source: Vec2d, space: Space):
        self.source = source
        self.space = space
        self.particles = []

    def limit_velocity(self, body, gravity, damping, dt):
        max_velocity = 400
        Body.update_velocity(body, gravity, damping, dt)
        l = body.velocity.length
        if l > max_velocity:
            scale = max_velocity / l
            body.velocity = body.velocity * scale

    def update_particles(self) -> None:
        print(f"Particles {len(self.particles)}")
        p = Particle(
            *self.source,
            3,
            self.space,
        )
        p.shape.elasticity = 1
        p.shape.friction = 1
        p.body.velocity_func = self.limit_velocity
        self.particles.append(p)
        for p in self.particles:
            p.lifetime -= 2
            p.color = (p.lifetime % 255, p.lifetime % 255, p.lifetime % 255)
            if not p.is_alive:
                try:
                    self.space.remove(p.body)
                    self.space.remove(p.shape)
                except AssertionError:
                    pass
                self.particles.remove(p)

    def render(self, display: Surface, camera_shift: Vec2d) -> None:
        for p in self.particles:
            p.render(display, camera_shift)


class ParticleScene(AbstractPymunkScene):

    pool: ParticlePool
    floor: RandomFloor

    def handle_event(self, event: Event) -> None:
        pass

    def reset_scene(self):
        super().reset_scene()
        self.pool = ParticlePool(Vec2d(250, 600), self.space)
        self.floor = RandomFloor(0, self.display.get_width(), 250, 250, 10, self.space)
        self.objects.extend((self.pool, self.floor))

    def update(self):
        super().update()
        self.pool.update_particles()
