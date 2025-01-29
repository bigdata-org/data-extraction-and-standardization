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
            
            

def remove_garbage():
    output_dir=Path('artifacts/docling')
    if output_dir.exists():
        shutil.rmtree(output_dir)