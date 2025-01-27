from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response
from utils.aws.s3 import get_s3_client, list_pdfs_from_s3, read_markdown_from_s3
from pydantic import BaseModel

app = FastAPI()

class s3MetaData(BaseModel):
    file_name: str
    file_size: int
    last_modified: str
    endpoint : str
                        

@app.get('/')
async def welcome():
    return {'msg':'Welcome to the / endpoint'}

@app.get('/objects')
async def fetch_s3_objects() -> s3MetaData :
    s3_client = get_s3_client()
    s3_meta = list_pdfs_from_s3(s3_client, container_name='uploads')
    return s3_meta

@app.get("/results/{id}")
async def fetch_md(id : str) :
    s3_client = get_s3_client()
    res = read_markdown_from_s3(s3_client, id)
    if len(res)==2:
        return {'markdown': res[0], 'endpoint' : res[1]}
    else:
        raise HTTPException(status_code=404, detail="Object not found")        
    

