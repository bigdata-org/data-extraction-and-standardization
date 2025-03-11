from fastapi import FastAPI, File, UploadFile, HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from tempfile import TemporaryDirectory
import os
import io
import boto3
from botocore.exceptions import ClientError
import pdfplumber
from PIL import Image
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

if not all([S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
    raise RuntimeError("Missing one or more required S3-related environment variables.")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def is_pdf_signature(file_bytes: bytes) -> bool:
    return file_bytes.startswith(b'%PDF-')

def upload_to_s3(file_path: str, s3_key: str) -> str:
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Error: {str(e)}")

def extract_pdf_text_images(pdf_path: str):
    markdown_content = []
    images = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                markdown_content.append(page_text)
            
            for image_index, img in enumerate(page.images):
                x0, top, x1, bottom = img["x0"], img["top"], img["x1"], img["bottom"]
                
                # Create a cropped page based on the bounding box
                cropped_page = page.crop((x0, top, x1, bottom))
                
                # Convert the cropped page to an image
                cropped_img = cropped_page.to_image(resolution=150)
                
                buffer = io.BytesIO()
                cropped_img.original.save(buffer, format="PNG")
                buffer.seek(0)
                
                images.append({
                    "content": buffer.getvalue(),
                    "mime_type": "image/png"
                })
    
    # Combine all extracted text
    full_markdown = "\n\n".join(markdown_content)
    return full_markdown, images

@app.post("/parse-pdf/")
async def parse_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported by filename")
    
    file_bytes = await file.read()
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File size exceeds 50MB limit")
    
    if not is_pdf_signature(file_bytes):
        raise HTTPException(status_code=400, detail="File content does not appear to be a valid PDF")
    
    with TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, file.filename)
        with open(pdf_path, 'wb') as temp_file:
            temp_file.write(file_bytes)
        
        try:
            markdown_text, images = await run_in_threadpool(extract_pdf_text_images, pdf_path)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        response_data = {
            "filename": file.filename,
            "markdown": markdown_text,
            "images": []
        }
        
        os.makedirs('images', exist_ok=True)
        
        for idx, image_data in enumerate(images):
            file_ext = image_data['mime_type'].split('/')[-1]
            local_filename = f"image_{idx + 1}.{file_ext}"
            local_path = os.path.join('images', local_filename)
            
            with open(local_path, 'wb') as img_file:
                img_file.write(image_data['content'])
            
            s3_key = f"pdf_images/{file.filename}/{local_filename}"
            s3_url = upload_to_s3(local_path, s3_key)
            
            response_data["images"].append({
                "index": idx + 1,
                "mime_type": image_data['mime_type'],
                "s3_url": s3_url,
                "filename": local_filename
            })
        
        # Append references to images at the end of the extracted text
        for img_info in response_data["images"]:
            response_data["markdown"] += f"\n\n![Extracted Image {img_info['index']}]({img_info['s3_url']})"
        
        return JSONResponse(content=response_data)
