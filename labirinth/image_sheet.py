from pathlib import Path
from typing import Iterable, Iterator, Tuple

import numpy as np
from PIL import Image


class ImageSheet:

    def __init__(self, images: Iterable[Iterator[np.ndarray]]):
        self.images = np.array(images)

    def create_sheet(self) -> Image.Image:
        rows, columns, h_image, w_image, _ = self.images.shape
        sheet = Image.new('RGB', (h_image * rows, w_image * columns))
        for y, group in enumerate(self):
            for x, image_array in enumerate(group):
                image_array = (image_array * 255)
                image = Image.fromarray(image_array)
                sheet.paste(image, (x * w_image, y * h_image))

        return sheet

    def save_to_image(self, path: str):
        path = Path(path)
        path.parent.mkdir(exist_ok=True, parents=True)
        sheet = self.create_sheet()
        sheet.save(path.with_suffix('.jpg'))

    def show(self, title: str):
        sheet = self.create_sheet()
        sheet.show(title)

    @classmethod
    def generate_black(cls, size: Tuple[int, int]) -> np.ndarray:
        return cls.generate_blank(*size)

    @classmethod
    def generate_white(cls, size: Tuple[int, int]) -> np.ndarray:
        return cls.generate_blank(*size, rgb_color=(1, 1, 1))

    @staticmethod
    def generate_blank(width: int, height: int, rgb_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        image = np.zeros((height, width, 3), np.uint8)
        image[:] = rgb_color
        return image

    def __iter__(self):
        return iter(self.images)

    def __getitem__(self, index):
        return self.images[index]

    def __setitem__(self, key, value):
        self.images[key] = value

    def __len__(self):
        return len(self.images)
