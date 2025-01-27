from fastapi import FastAPI, UploadFile, File, Request, Response
from backend.utils.aws.s3 import get_s3_client, list_pdfs_from_s3
from pydantic import BaseModel

app = FastAPI()

@app.get('/')
async def welcome():
    return {'msg':'Welcome to the / endpoint'}

@app.get('/objects')
async def fetch_s3_objects():
    s3_client = get_s3_client()
    s3_meta = list_pdfs_from_s3(s3_client, container_name='uploads')
    return s3_meta
        
    

