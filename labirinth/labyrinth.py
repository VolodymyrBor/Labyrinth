import math
import logging
from io import BytesIO
from random import choice
from collections import deque
from operator import attrgetter, itemgetter
from typing import List, overload, Union, Iterable

import numpy as np
from PIL import Image
from tqdm import tqdm

from .matrix import Matrix
from .gif import DynamicGIF
from .utils import is_even, Coord
from .image_sheet import ImageSheet
from .settings import WALL, VISITED, ENTER, EMPTY, SUPPORT_EXTENSIONS


class LabyrinthError(Exception):
    pass


class Labyrinth:

    def __init__(self, height: int = 5, width: int = 5, lab: Iterable[Iterable[str]] = None):
        self._height = height
        self._width = width
        self.logger = logging.getLogger(type(self).__name__)

        self._labyrinth = []
        if lab is not None:
            self._labyrinth = np.array(lab)

        if not lab:
            self.generate_empty()

    def generate_empty(self):
        self._labyrinth = np.array([
            [self.get_cell(col, row) for col in range(self._width)]
            for row in range(self._height)
        ])

    def generate(self, start_coord: Coord = Coord(1, 1)):

        matrix = self.get_matrix()
        matrix.visit(start_coord)

        current_coord = start_coord
        coords_queue = deque()
        status = tqdm(total=len(matrix.get_not_visited()), desc='Lab generating', unit='Cell')
        while matrix.get_not_visited():
            neighborhood = current_coord.neighborhood(2)
            neighborhood = filter(self.is_legal, neighborhood)
            not_visited_neighborhood = list(filter(matrix.is_not_visited, neighborhood))

            if not_visited_neighborhood:
                coords_queue.append(current_coord)
                neighbor = choice(not_visited_neighborhood)
                self.remove_wall_between(current_coord, neighbor)
                matrix.visit(neighbor)
                status.update()
                current_coord = neighbor
            elif coords_queue:
                current_coord = coords_queue.popleft()
            else:
                not_visited = matrix.get_not_visited()
                current_coord = choice(not_visited)
                matrix.visit(current_coord)
                status.update()

        self.create_enter(0)
        self.create_enter(-1)

    def is_wall(self, coord: Coord) -> bool:
        return self[coord] in [WALL, VISITED]

    def is_empty(self, coord: Coord) -> bool:
        return not self.is_wall(coord)

    def is_legal(self, coord: Coord) -> bool:
        x, y = coord
        return 0 < x < self._width - 1 and 0 < y < self._height - 1

    def remove_wall_between(self, coord1: Coord, coord2: Coord):
        coords = (coord1, coord2)
        if coord1.x == coord2.x:
            coord = min(coords, key=attrgetter('y'))
            mid_coord = coord.to_down()
        elif coord1.y == coord1.y:
            coord = min(coords, key=attrgetter('x'))
            mid_coord = coord.to_right()
        else:
            raise Exception('Coords must be in one line.')

        self[mid_coord] = EMPTY

    def generate_image(self, block_size: int = 64) -> ImageSheet:
        image_shape = (block_size, block_size)
        white_image = ImageSheet.generate_white(image_shape)
        black_image = ImageSheet.generate_black(image_shape)
        red_image = ImageSheet.generate_blank(block_size, block_size, (1, 0, 0))

        image_mapping = {
            EMPTY: white_image,
            WALL: black_image,
            ENTER: red_image,
        }

        images = [
            [image_mapping[el] for el in row]
            for row in self
        ]

        sheet = ImageSheet(images)
        return sheet

    def save_as_image(self, path: str, block_size: int = 64):
        sheet = self.generate_image(block_size)
        sheet.save_to_image(path)

    def save_as_bytes_io(self, block_size: int = 64) -> BytesIO:
        sheet = self.generate_image(block_size)
        image = sheet.create_sheet()
        image_io = BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)

        return image_io

    def show(self, block_size: int = 64, title: str = 'Labyrinth'):
        sheet = self.generate_image(block_size)
        sheet.show(title)

    def create_enter(self, col: int) -> Coord:
        lab = [row[1:-1] for row in self]
        column = map(itemgetter(col), lab)
        empty_cell = [i for i, cell in enumerate(column) if cell == EMPTY]
        row_idx = choice(empty_cell)
        cord_enter = Coord(col, row_idx)
        self[cord_enter] = ENTER
        return cord_enter

    def find_enter(self, col: int) -> Coord:

        for y, row in enumerate(self._labyrinth):
            for x, el in enumerate(row):
                if el == ENTER:
                    coord = Coord(x, y)
                    self[coord] = EMPTY
                    return coord

        self.logger.debug(f'Enter not found.')
        return self.create_enter(col)

    def solve(self, enter_col: int = 0, exit_col: int = -1):
        way = self.get_solved_way(enter_col, exit_col)
        self.mark_solve_from_way(way)

    def solve_with_gif(self, path: str, block_size: int = 8, enter_col: int = 0, exit_col: int = -1):

        way = self.get_solved_way(enter_col, exit_col)

        with DynamicGIF() as gif:
            for coord in tqdm(way, desc='Creating GIF', unit='Image'):
                self.mark_solve_from_way([coord])
                sheet = self.generate_image(block_size)
                snapshot = sheet.create_sheet()
                gif.append(snapshot)
            gif.save_gif(path)

    def get_solved_way(self, enter_col: int = 0, exit_col: int = -1) -> List[Coord]:
        matrix = self.get_matrix()
        start = self.find_enter(enter_col)
        end = self.find_enter(exit_col)
        way = [start, *matrix.bfs(start, end), end]
        return way

    def mark_solve_from_way(self, way: Iterable[Coord]):
        for coord in way:
            self[coord] = ENTER

    def get_matrix(self) -> Matrix:
        matrix = Matrix([
            [1 if el == WALL else 0 for el in row]
            for row in self._labyrinth
        ])
        return matrix

    @staticmethod
    def get_cell(col: int, row: int) -> str:
        if is_even(row) or is_even(col):
            return WALL
        return EMPTY

    @classmethod
    def from_pil_image(cls, image: Image.Image) -> 'Labyrinth':
        image = image.convert('RGB')
        w, h = image.size
        binary = image.point(lambda p: p > 128)
        array = np.array(binary)
        block_size = cls.recognize_block_size(array)
        lab = np.array([
            [
                cls.get_element(array[i: i + block_size, j: j + block_size])
                for j in range(0, h, block_size)
            ]
            for i in range(0, w, block_size)
        ])
        return Labyrinth(*lab.shape, lab=list(lab))

    @classmethod
    def from_image(cls, path: str) -> 'Labyrinth':
        image: Image.Image = Image.open(path)
        return cls.from_pil_image(image)

    @staticmethod
    def get_element(image: np.ndarray) -> str:
        if all(image[:, :, i].any() for i in range(3)):
            return EMPTY
        elif image[:, :, :1].any():
            return ENTER
        else:
            return WALL

    @staticmethod
    def recognize_block_size(array: np.ndarray) -> int:
        block_size = math.inf
        counter = 0
        h, w = array.shape[:2]
        with tqdm(total=h * w, desc='Recognize blocks size.') as status:
            for row in array:
                previous: np.ndarray = row[0]
                for current in row:
                    if np.ndarray.all(current == previous):
                        counter += 1
                    else:
                        block_size = min(block_size, counter)
                        counter = 1
                    previous = current
                    status.update()
                else:
                    block_size = min(block_size, counter)
                    counter = 0

        if block_size == math.inf:
            raise LabyrinthError('Can not recognize block_size.')

        if block_size not in SUPPORT_EXTENSIONS:
            raise LabyrinthError(f'Block size : {block_size} is not supported.')

        return block_size

    def __str__(self):
        return str('\n'.join(map(str, self._labyrinth)))

    @overload
    def __getitem__(self, index: Coord) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> List[List[str]]: ...

    def __getitem__(self, index: Union[int, slice, Coord]) -> List[str]:
        if isinstance(index, Coord):
            x, y = index
            return self._labyrinth[y][x]

        return self._labyrinth[index]

    def __setitem__(self, key: Union[int, Coord], value):
        if isinstance(key, Coord):
            self._labyrinth[key.y][key.x] = value
        else:
            self._labyrinth[key] = value

    def __iter__(self):
        return iter(self._labyrinth)
