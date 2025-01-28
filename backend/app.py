from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response
from backend.utils.aws.s3 import *
from backend.utils.docling.core import PDF2MD as docling_PDF2MD
from backend.utils.firecrawl.core import get_firecrawl_client,scraper
from backend.utils.azure.document_intelligence import get_doc_int_client, extracter as docint_extracter
from backend.utils.helper import is_valid_url, remove_garbage
from pydantic import BaseModel
from typing import List
import io
from  dotenv import load_dotenv

load_dotenv()
app = FastAPI()

class s3MetaData(BaseModel):
    file_name: str
    file_size: int
    last_modified: str
    url : str

class MarkdownModel(BaseModel):
    md: str
    url: str
        
class UrlModel(BaseModel):
    url: str
                        

@app.get('/')
async def welcome():
    return {'msg':'Welcome to the / endpoint'}

@app.get('/objects')
async def fetch_s3_objects() -> List[s3MetaData] :
    s3_client = get_s3_client()
    s3_meta = list_pdfs_from_s3(s3_client, container_name='uploads')
    return s3_meta

@app.get('/results/docling/{id}')
async def fetch_docling_md(id : str) -> MarkdownModel:
    s3_client = get_s3_client()
    res = read_markdown_from_s3(s3_client, id)
    if not isinstance(res,int):
        return {'markdown': res[0].decode('utf-8'), 'url' : res[1]}
    else:
        raise HTTPException(status_code=404, detail="Object not found")
    
@app.post('/upload')
async def upload_pdf(file_bytes_io) -> UrlModel:
    s3_client = get_s3_client()
    endpoint = upload_pdf_to_s3(s3_client, file_bytes_io)
    if endpoint==-1:
        raise HTTPException(status_code=500, detail="Internel Server Error")
    else:
        return {"url": endpoint}
    
@app.post('/extract/docling') 
async def extract_docling_md(request: UrlModel) -> UrlModel:
    url = request.url
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="bad request")
    else:
        s3_client = get_s3_client()
        endpoint = docling_PDF2MD(s3_client, url)
        return {"url": endpoint}

@app.post('/extract/doc-int')
async def docint_extract(request: UrlModel):
    url = request.url
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="bad request")
    else:
        docint_client, s3_client = get_doc_int_client(), get_s3_client()   
        log = docint_extracter(doc_int_client=docint_client, s3_client=s3_client, url = url)
        return log
    
@app.post('/scrape/firecrawl')        
async def firecrawl_scrape(request: UrlModel) -> MarkdownModel:
    url = request.url
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="bad request")
    else:
        s3_client, firecrawl_client = get_s3_client(), get_firecrawl_client()
        res = scraper(s3_client, firecrawl_client,url)
        if isinstance(res, int):
            return HTTPException(status_code=500, detail="Internel Server Error")
        else:
            return {'markdown': res[0].decode('utf-8'), 'url' : res[1]}

@app.post('/scrape/bs')        
async def firecrawl_scrape(request: UrlModel) -> MarkdownModel:
    url = request.url
    if not is_valid_url(url):
        raise HTTPException(status_code=400, detail="bad request")
    else:
        #must change the next 2 lines of code, for BS implementation
        s3_client, firecrawl_client = get_s3_client(), get_firecrawl_client()
        res = scraper(s3_client, firecrawl_client,url)
        if isinstance(res, int):
            return HTTPException(status_code=500, detail="Internel Server Error")
        else:
            return {'markdown': res[0].decode('utf-8'), 'url' : res[1]}
        
@app.get('/protected/cleanup')
async def cleanup(secret: str):
    if secret=='_101x':
        remove_garbage()
        return {"status_code":200, "detail":"OK"}
    else:
        raise HTTPException(status_code=400, detail="bad request") 



