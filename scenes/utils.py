from typing import Tuple, Union

from pymunk.vec2d import Vec2d


def convert(vector: Union[Tuple[int | float, int | float], Vec2d], screen_h: int) -> Tuple[int, int]:
    x, y = vector
    return int(x), screen_h - int(y)
