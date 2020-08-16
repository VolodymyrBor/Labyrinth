import uuid
from pathlib import Path
from typing import Iterable, Iterator
from tempfile import TemporaryDirectory

import imageio
from tqdm import tqdm
from PIL import Image


class DynamicGIF:

    def __init__(self, images: Iterable[Image.Image] = None):
        self.temp_dir = TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.image_paths = list(self._save_images(images)) if images else []

    def update(self, image: [Image.Image], index: int):
        path = self._save_image(image)
        self.image_paths[index] = path

    def append(self, image: Image.Image):
        path = self._save_image(image)
        self.image_paths.append(path)

    def pop(self, index: int) -> Path:
        return self.image_paths.pop(index)

    def save_gif(self, path: str):
        path = Path(path).with_suffix('.gif')
        status = tqdm(total=len(self), desc='Saving GIF', unit='Image')
        with imageio.get_writer(path) as writer:
            for path in self.image_paths:
                image = imageio.imread(path)
                writer.append_data(image)

                status.update()

    def clear(self):
        self.image_paths = []
        self.temp_dir.cleanup()

    def _save_image(self, image: Image.Image) -> Path:
        image_name = self._create_image_name()
        path = self.base_path.with_name(image_name).with_suffix('.jpg')
        image.save(path)
        return path

    def _save_images(self, images: Iterable[Image.Image]) -> Iterator[Path]:
        return map(self._save_image, images)

    @staticmethod
    def _create_image_name() -> str:
        return str(uuid.uuid4())

    def __len__(self):
        return len(self.image_paths)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
