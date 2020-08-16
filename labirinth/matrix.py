from collections import deque
from typing import overload, Union, List, Iterable

import numpy as np
from tqdm import tqdm

from .utils import Coord
from .settings import VISITED


class Matrix:

    def __init__(self, matrix: Iterable[Iterable[int]]):
        self.matrix = list(map(list, matrix))

    def is_visited(self, coord: Coord) -> bool:
        return self[coord] == VISITED

    def is_not_visited(self, coord: Coord) -> bool:
        return not self.is_visited(coord)

    def visit(self, coord: Coord):
        self[coord] = VISITED

    def get_not_visited(self) -> List[Coord]:
        coords = []
        for y, row in enumerate(self):
            for x, el in enumerate(row):
                coord = Coord(x, y)
                if self.is_not_visited(coord):
                    coords.append(coord)
        return coords

    def bfs(self, start: Coord, end: Coord) -> Iterable[Coord]:

        start = start.normalize(self.shape)
        end = end.normalize(self.shape)

        way_map = Matrix([[0 for _ in row] for row in self])
        dq = deque([start])
        self.visit(start)
        status = tqdm(total=len(self.get_not_visited()), desc='BFS', unit='Cell')
        while dq:
            current: Coord = dq.popleft()
            neighborhood = current.neighborhood()
            neighborhood = filter(self.is_legal, neighborhood)
            not_visited_neighborhood = list(filter(self.is_not_visited, neighborhood))

            if not_visited_neighborhood:
                dq.extend(not_visited_neighborhood)
                for neighbor in not_visited_neighborhood:
                    way_map[neighbor] = current
                    self.visit(neighbor)
                    status.update()
                    if neighbor == end:
                        return self.generate_way(current, way_map)
        return []

    @staticmethod
    def generate_way(current: Coord, way_map: 'Matrix') -> Iterable[Coord]:
        way = []
        while isinstance(current, Coord):
            way.append(current)
            current = way_map[current]
        way.reverse()
        return way

    def is_legal(self, coord: Coord) -> bool:
        h, w = self.shape
        return 0 <= coord.x < w and 0 <= coord.y < h

    @property
    def shape(self) -> tuple:
        return np.array(self.matrix).shape

    def __iter__(self):
        return iter(self.matrix)

    @overload
    def __getitem__(self, index: Coord) -> int: ...

    @overload
    def __getitem__(self, index: slice) -> List[List[int]]: ...

    def __getitem__(self, index: Union[int, slice, Coord]) -> List[int]:
        if isinstance(index, Coord):
            x, y = index
            try:
                return self.matrix[y][x]
            except IndexError:
                pass

        return self.matrix[index]

    def __setitem__(self, key: Union[int, Coord], value):
        if isinstance(key, Coord):
            self.matrix[key.y][key.x] = value
        else:
            self.matrix[key] = value
