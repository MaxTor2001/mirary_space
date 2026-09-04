"""Уменьшение картинок товаров: снимок с телефона весит мегабайты."""
from io import BytesIO
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

FULL_SIDE = 1600   # для страницы товара
THUMB_SIDE = 480   # для карточки в каталоге
QUALITY = 82


def encode(data, max_side):
    """Ужимает картинку до max_side по длинной стороне и отдаёт её как JPEG."""
    image = Image.open(BytesIO(data))
    image = ImageOps.exif_transpose(image)  # телефон хранит поворот в EXIF
    image = image.convert("RGB")
    image.thumbnail((max_side, max_side), Image.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    return ContentFile(buffer.getvalue())


def basename(path):
    """Имя файла без каталога: upload_to приклеивается к нему повторно."""
    return PurePosixPath(path).name


def thumb_filename(image_name):
    """Имя миниатюры выводится из имени оригинала — по нему видно, устарела ли она."""
    return f"{PurePosixPath(image_name).stem}.jpg"
