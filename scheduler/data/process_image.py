import os
import pathlib
from PIL import Image
from scheduler.config import IMAGES_DIR, STANDARD_IMAGE_SIZE


def process_image(name: str, result: str):
    img = Image.open(name)
    extension = pathlib.Path(name).suffix
    img.resize(STANDARD_IMAGE_SIZE).save(os.path.join(IMAGES_DIR, result + extension))
