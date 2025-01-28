import validators
import shutil
from pathlib import Path

def is_valid_url(url: str) -> bool:
    return validators.url(url)

def remove_garbage():
    output_dir=Path('artifacts/docling')
    if output_dir.exists():
        shutil.rmtree(output_dir)