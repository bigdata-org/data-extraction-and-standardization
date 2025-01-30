import validators
import shutil
from pathlib import Path

def is_valid_url(url: str) -> bool:
    return validators.url(url)

def parse_endpoints(lst):
    res = {'tables':[], 'images':[]}
    for url in lst:
        if '/images/' in url['url']:
            res['images'].append(url)
        else:
            res['tables'].append(url)
    return res

def is_file_size_within_limit(file_bytes_io, max_size_mb: int = 5) -> bool:
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = file_bytes_io.getbuffer().nbytes  # Get the size of the file
    
    if file_size > max_size_bytes:
        return False  # File size exceeds the limit
    return True  # File size is within the limit
            
            

def remove_garbage():
    output_dir=Path('artifacts/docling')
    if output_dir.exists():
        shutil.rmtree(output_dir)