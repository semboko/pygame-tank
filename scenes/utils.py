from typing import List, Sequence, Tuple, Union

from pymunk.vec2d import Vec2d


def convert(vector: Union[Tuple[int | float, int | float], Vec2d], screen_h: int) -> Tuple[int, int]:
    x, y = vector
    return int(x), screen_h - int(y)


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
