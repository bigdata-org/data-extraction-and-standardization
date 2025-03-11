from fastapi import FastAPI, HTTPException, UploadFile, File
from utils.aws.s3 import *
from utils.opensource.pdf.core import extracter as oss_exrtacter
from utils.opensource.web.core import scraper as oss_scraper
from utils.docling.core import PDF2MD as docling_PDF2MD
from utils.firecrawl.core import get_firecrawl_client, scraper
from utils.azure.document_intelligence import get_doc_int_client, extracter as docint_extracter
from utils.haystack.pipeline import summarize, qa
from utils.helper import *
from pydantic import BaseModel
from typing import List
from io import BytesIO
from  dotenv import load_dotenv
import redis

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

class CsvImageUrlModel(BaseModel):
    images: list
    tables: list


class CsvImageUrlMdModel(BaseModel):
    tables: list
    images: list
    md : str
    
class TextSummaryModel(BaseModel):
    url: str
    model: str

class qaModel(BaseModel):
    url: str
    model: str
    prompt: str    
    
# Redis Client for Database 0
redis_client_db0 = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Redis Client for Database 1
redis_client_db1 = redis.StrictRedis(host='localhost', port=6379, db=1, decode_responses=True)
                  

@app.get('/')
async def welcome():
    return {'msg':'Welcome to the / endpoint'}

@app.get('/objects')
async def fetch_s3_objects() -> List[s3MetaData] :
    try:
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_s3_error()
        s3_meta = list_pdfs_from_s3(s3_client, container_name='uploads')
        if isinstance(s3_meta, int):
            raise handle_internal_server_error()
        return s3_meta
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

@app.get('/results/docling/{id}')
async def fetch_docling_md(id : str) -> MarkdownModel:
    try:
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_s3_error()
        res = read_markdown_from_s3(s3_client, id)
        if isinstance(res, int):
            raise handle_object_not_found()
        return {'md': res[0].decode('utf-8'), 'url': res[1]}
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()
    
@app.get('/results/doc-int/{id}')
async def fetch_doc_int_endpoints(id : str) -> CsvImageUrlModel:
    try:
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_s3_error()
        res = list_endpoints_from_s3(s3_client, f'results/azure-ai-document-intelligence/{id}')
        if isinstance(res, int):
            raise handle_internal_server_error()
        elif isinstance(res, list) and len(res) == 0:
            raise handle_object_not_found()
        else:
            parsed_endpoints = parse_endpoints(res, mode=1)
            return parsed_endpoints
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()
    
@app.get('/results/opensource/{id}')
async def fetch_oss_endpoints(id : str) -> CsvImageUrlModel:
    try:
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_internal_server_error("S3 client is down")
        res = list_endpoints_from_s3(s3_client, f'results/opensource/{id}')
        if isinstance(res, int):
            raise handle_internal_server_error()
        elif isinstance(res, list) and len(res) == 0:
            raise handle_object_not_found()
        else:
            parsed_endpoints = parse_endpoints(res, mode=1)
            return parsed_endpoints
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

# Upload PDF endpoint
@app.post('/upload')
async def upload_pdf(file: UploadFile = File(...)) -> UrlModel:
    try:
        file_content = await file.read()
        if not is_file_size_within_limit(file_content):
            handle_invalid_file_size()
        try:
            file_bytes_io = BytesIO(file_content)
        except Exception as e:
            handle_invalid_pdf()
        s3_client = get_s3_client()
        if s3_client == -1:
            handle_s3_error()
        endpoint = upload_pdf_to_s3(s3_client, file_bytes_io)
        if endpoint == -1:
            handle_internal_server_error()
        return {"url": endpoint}
    except HTTPException as e:
        raise e
    except Exception as e:
        handle_internal_server_error()
    
@app.post('/extract/docling') 
async def extract_docling_md(request: UrlModel) -> UrlModel:
    try:
        url = request.url
        if not is_valid_url(url):
            raise handle_invalid_url()
        s3_client = get_s3_client()
        endpoint = docling_PDF2MD(s3_client, url)
        if isinstance(endpoint, int):
            raise handle_internal_server_error()
        return {"url": endpoint}
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

@app.post('/extract/doc-int')
async def docint_extract(request: UrlModel) -> CsvImageUrlModel:
    try:
        url = request.url
        if not is_valid_url(url):
            raise handle_invalid_url()
        docint_client, s3_client = get_doc_int_client(), get_s3_client()
        if docint_client == -1:
            raise handle_internal_server_error("Azure client is down")
        if s3_client == -1:
            raise handle_internal_server_error("S3 client is down")
        raw_log = docint_extracter(doc_int_client=docint_client, s3_client=s3_client, url=url)
        return raw_log
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()
    
@app.post('/extract/opensource')
async def oss_extract(request: UrlModel) -> CsvImageUrlModel:
    try:
        url = request.url
        if not is_valid_url(url):
            raise handle_invalid_url()
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_s3_error()
        raw_log = oss_exrtacter(s3_client, url)
        return raw_log
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()
    
@app.post('/scrape/firecrawl')        
async def firecrawl_scrape(request: UrlModel) -> MarkdownModel:
    try:
        url = request.url
        if not is_valid_url(url):
            raise handle_invalid_url()
        s3_client, firecrawl_client = get_s3_client(), get_firecrawl_client()
        if s3_client == -1:
            raise handle_internal_server_error("S3 client is down")
        if firecrawl_client == -1:
            raise handle_internal_server_error("Firecrawl client is down")
        res = scraper(s3_client, firecrawl_client, url)
        if isinstance(res, int):
            raise handle_internal_server_error()
        return {'md': res[0], 'url': res[1]}
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

@app.post('/scrape/bs')        
async def bs_scrape(request: UrlModel) -> CsvImageUrlMdModel:
    try:
        url = request.url
        if not is_valid_url(url):
            raise handle_invalid_url()
        s3_client = get_s3_client()
        if s3_client == -1:
            raise handle_internal_server_error("S3 client is down")
        res = oss_scraper(s3_client, url)
        if isinstance(res, int):
            raise handle_internal_server_error()
        return res
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

@app.post('/text-summarize') 
async def text_summarization(request: TextSummaryModel) :
    try:
        url = request.url
        model = request.model
        if not is_valid_url(url):
            raise handle_invalid_url()
        if invalid_model(model):
            raise handle_invalid_model()
        s3_client = get_s3_client()
        response = summarize(s3_client, url, model) if model else summarize(s3_client, url)
        log = response.copy()  
        log.pop('markdown', None)
        log_id = log.get('id')  
        if log_id:  # Check if the 'id' is available
            redis_client_db0.set(log_id, str(log))
        return {"markdown": response['markdown']}
    except HTTPException as e:
        raise e
    except Exception as e:
        # raise handle_internal_server_error()
        raise e
    
@app.post('/qa') 
async def qa_pipeline(request: qaModel):
    try:
        url = request.url
        model = request.model
        prompt = request.prompt
        if not is_valid_url(url):
            raise handle_invalid_url()
        if invalid_model(model):
            raise handle_invalid_model()
        if invalid_prompt(prompt):
            raise handle_invalid_prompt()
        s3_client = get_s3_client()
        response = qa(s3_client, url, prompt, model) if model else qa(s3_client, url, prompt)
                # Create a log dictionary (clone the response and remove markdown)
        log = response.copy()  
        log.pop('markdown', None)
        log_id = log.get('id')  
        if log_id:  # Check if the 'id' is available
            redis_client_db1.set(log_id, str(log))
        return {"markdown": response['markdown']}
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()

        
@app.get('/protected/cleanup')
async def cleanup(secret: str):
    try:
        if secret == '_101x':
            remove_garbage()
            return {"status_code": 200, "detail": "OK"}
        else:
            raise handle_invalid_url()
    except HTTPException as e:
        raise e
    except Exception:
        raise handle_internal_server_error()


@app.get("/get_all_db0")
async def get_all_keys_db0():
    try:
        keys = redis_client_db0.keys('*')  # Get all keys in DB 0
        if not keys:
            return {"message": "No keys found in DB 0."}
        return {"keys": keys}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_all_db1")
async def get_all_keys_db1():
    try:
        keys = redis_client_db1.keys('*')  # Get all keys in DB 1
        if not keys:
            return {"message": "No keys found in DB 1."}
        return {"keys": keys}
    except Exception as e:
        return {"error": str(e)}

