from PIL.Image import Image

from labirinth import Labyrinth
from labirinth.utils import is_even


def generate_lab(size: int) -> Labyrinth:
    if is_even(size):
        size += 1

    lab = Labyrinth(height=size, width=size)
    lab.generate()
    return lab


def solve_lab(image: Image) -> Labyrinth:
    lab = Labyrinth.from_image(image, block_size=8)
    lab.solve()
    return lab
