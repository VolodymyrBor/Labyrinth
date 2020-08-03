import cv2
import numpy as np
from PIL import Image

SIZE = 3

image: Image.Image = Image.open('lab7.jpg')
# image = image.convert('L')

w, h = image.size

binary = image.point(lambda p: p > 128)

array = np.array(binary)

print(array[:SIZE, :SIZE])


matrix = []

for i in range(0, w, SIZE):
    row = []
    for j in range(0, h, SIZE):
        block: np.ndarray = array[i: i + SIZE, j: j + SIZE]
        if block.any():
            row.append(0)
        else:
            row.append(1)
    matrix.append(row)

for row in matrix:
    print(row)
