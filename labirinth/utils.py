from typing import NamedTuple, Tuple


def is_even(x: int) -> bool:
    return x % 2 == 0


def is_odd(x: int) -> bool:
    return not is_even(x)


class Coord(NamedTuple):
    x: int
    y: int

    def to_top(self, n: int = 1) -> 'Coord':
        return Coord(self.x, self.y - 1 * n)

    def to_down(self, n: int = 1) -> 'Coord':
        return Coord(self.x, self.y + 1 * n)

    def to_left(self, n: int = 1) -> 'Coord':
        return Coord(self.x - 1 * n, self.y)

    def to_right(self, n: int = 1) -> 'Coord':
        return Coord(self.x + 1 * n, self.y)

    def neighborhood(self, n: int = 1):
        return (
            self.to_top(n),
            self.to_down(n),
            self.to_left(n),
            self.to_right(n),
        )

    def normalize(self, size: Tuple[int, int]) -> 'Coord':
        t = tuple(self.coord_normalize(x, l) for x, l in zip(self, reversed(size)))
        return Coord(*t)

    @staticmethod
    def coord_normalize(x, limit) -> int:
        if x >= 0:
            return x

        return limit + x

