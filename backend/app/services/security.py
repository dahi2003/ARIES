import imghdr
from fastapi import HTTPException, status
from pathlib import Path
from typing import Iterable

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}
ALLOWED_IMAGE_TYPES = {'png', 'jpeg'}


def validate_upload_filename(filename: str) -> None:
    if '.' not in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Missing file extension')
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Invalid file type: {extension}')


def validate_file_content(path: Path) -> None:
    if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
        image_type = imghdr.what(path)
        if image_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Uploaded image is not a valid PNG/JPEG file')


def scan_for_viruses(path: Path) -> None:
    # Placeholder stub for integration with commercial file scanning solutions.
    if path.stat().st_size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Empty file cannot be processed')


def validate_bulk_files(files: Iterable[Path]) -> None:
    for file in files:
        validate_upload_filename(file.name)
        validate_file_content(file)
        scan_for_viruses(file)
