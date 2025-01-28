from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response
from utils.aws.s3 import get_s3_client, list_pdfs_from_s3, read_markdown_from_s3
from utils.firecrawl.core import get_firecrawl_client,scraper
from utils.helper import is_valid_url
from pydantic import BaseModel
from  dotenv import load_dotenv

load_dotenv()
app = FastAPI()

class s3MetaData(BaseModel):
    file_name: str
    file_size: int
    last_modified: str
    endpoint : str

class doclingMarkdownModel(BaseModel):
    markdown: str
    endpoint: str
        
class ScrapeRequest(BaseModel):
    url: str
                        

@app.get('/')
async def welcome():
    return {'msg':'Welcome to the / endpoint'}

@app.get('/objects')
async def fetch_s3_objects() -> s3MetaData :
    s3_client = get_s3_client()
    s3_meta = list_pdfs_from_s3(s3_client, container_name='uploads')
    return s3_meta

@app.get('/results/docling/{id}')
async def fetch_md(id : str) -> doclingMarkdownModel:
    s3_client = get_s3_client()
    res = read_markdown_from_s3(s3_client, id)
    if not isinstance(res,int):
        return {'markdown': res[0].decode('utf-8'), 'endpoint' : res[1]}
    else:
        raise HTTPException(status_code=404, detail="Object not found")
    
@app.post('/scrape/firecrawl')        
async def scrape_webpage(request: ScrapeRequest):
    url = request.url
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="bad request")
    else:
        s3_client, firecrawl_client = get_s3_client(), get_firecrawl_client()
        endpoint = scraper(s3_client, firecrawl_client,url)
        if endpoint==-1:
            return { "error": "Internal Server Error", "message": "Something went wrong on the server. Please try again later."}
        else:
            return {"endpoint" : endpoint}
     

