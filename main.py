from pathlib import Path

from labirinth.utils import Coord
from labirinth.labyrinth import Labyrinth


def create_lab(path: str, size: int = 65):
    path = Path(path)
    path_solved = path.with_name(path.name + '_solved')

    lab = Labyrinth(height=size, width=size)
    lab.generate(Coord(1, 1))
    lab.save_as_image(path)
    lab.show()

    # solve
    lab.solve()
    lab.save_as_image(path_solved)
    lab.show()


def solve_lab_from_image(path: str, block_size: int = 64):
    path = Path(path)
    path_solved = path.with_name(path.name + '_solved')

    lab = Labyrinth.from_image('lasd.jpg')
    lab.show(block_size)
    lab.solve()
    lab.show(block_size)
    lab.save_as_image(path_solved, block_size)


def main():
    lab = Labyrinth(11, 11)
    lab.generate(Coord(1, 1))
    lab.save_as_image('new')
    # lab.solve_with_gif('solve-mini')

    # lab = Labyrinth.from_image()
    # lab.show()
    # lab.solve_with_gif('maral', block_size=1)
    # lab.save_as_image('for-maral')


if __name__ == '__main__':
    # create_lab('NEW_LAB')
    # solve_lab_from_image('Labyrinth.jpg')
    main()
