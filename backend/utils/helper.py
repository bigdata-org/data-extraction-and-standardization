import validators
import shutil
from pathlib import Path
from fastapi import  HTTPException

def is_valid_url(url: str) -> bool:
    return validators.url(url)

def parse_endpoints(lst, mode=0):
    res = {'tables':[], 'images':[]}
    if mode==0:
        for data in lst:
            if '/images/' in data['url']:
                res['images'].append(data)
            else:
                res['tables'].append(data)
    else:
        for data in lst:
            if data['file_name'].endswith('.csv'):
                res['tables'].append(data)
            else:
                res['images'].append(data)
    return res
                
            
def is_file_size_within_limit(file_bytes, max_size_mb: int = 5) -> bool:
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    file_size = len(file_bytes)  # Get the size of the file
    
    if file_size > max_size_bytes:
        return False  # File size exceeds the limit
    return True  # File size is within the limit

def invalid_prompt(prompt: str) -> bool:
    if not prompt or not isinstance(prompt, str):
        return True  # Invalid prompt
    if len(prompt.strip()) == 0:  # Empty or whitespace-only prompt
        return True
    if len(prompt) > 500:  # Example constraint: Max length of 500 characters
        return True
    return False

def invalid_model(model: str) -> bool:
    if not model or not isinstance(model, str):
        return True  # Invalid prompt
    if len(model.strip()) == 0:  # Empty or whitespace-only prompt
        return True
    return False
            
def remove_garbage():
    output_dir=Path('artifacts/docling')
    if output_dir.exists():
        shutil.rmtree(output_dir)
        
        
def handle_invalid_file_size():
    raise HTTPException(status_code=400, detail="File size exceeds 5 MB")

def handle_invalid_url():
    raise HTTPException(status_code=400, detail="Invalid URL")

def handle_object_not_found():
    raise HTTPException(status_code=400, detail="Object Not Found")

def handle_invalid_pdf():
    raise HTTPException(status_code=400, detail="Invalid or corrupted PDF file")

def handle_s3_error():
    raise HTTPException(status_code=500, detail="S3 bucket is currently not accessible")

def handle_internal_server_error(detail="Internal Server Error"):
    raise HTTPException(status_code=500, detail=detail)

def handle_invalid_prompt():
    raise HTTPException(status_code=400, detail="Invalid prompt. Please provide a valid text prompt.")

def handle_invalid_model():
    raise HTTPException(status_code=400, detail="Invalid Model. Please provide a valid model.")