import os
from io import BytesIO
import requests
import boto3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import hashlib
import json
from io import StringIO
from backend.utils.aws.s3 import write_image_to_s3_nopage, write_dataframe_to_s3_nopage
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling_core.types.doc import ImageRefMode


def scraper(s3_client, url):
    try:
        log={'images':[], 'tables':[], 'md': ''}
        parent_file = hashlib.sha256(url.encode()).hexdigest()
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        i_trace = scrape_images(s3_client, soup, parent_file)
        if not isinstance(i_trace,int):
            log['images']=i_trace
        t_trace = scrape_tables(s3_client, soup, parent_file)
        if t_trace!=-1:
            log['tables']=t_trace
        log['md'] = web2md(soup, parent_file )
        return log
    except:
        return -1

def scrape_images(s3_client, soup, parent_file):
    trace=[]
    try:
        img_tags = soup.find_all('img')
        for i,img_tag in enumerate(img_tags):
            img_url = img_tag.get('src')
            if img_url:
                try:
                    img_bytes = requests.get(img_url).content
                    public_url = write_image_to_s3_nopage(channel='bs',s3_client=s3_client, image_bytes=img_bytes, parent_file=parent_file, id=i+1 )
                    img_tag['src'] = public_url
                    trace.append(public_url) if public_url!=-1 else trace.append(f'(Error) Cannot process : {img_url}')
                except Exception as e:
                    trace.append(f'(Error) GET Request Failed : {img_url}')
        return trace
    except Exception as e:
        return -1

def scrape_tables(s3_client, soup, parent_file):
    tables = soup.find_all('table')
    trace = []
    for i, table in enumerate(tables):
        try:
            # Wrap the table HTML string in StringIO before passing to pd.read_html
            df = pd.read_html(StringIO(str(table)))[0]
            public_url = write_dataframe_to_s3_nopage(channel='bs', s3_client=s3_client, df=df, parent_file=parent_file, id=i+1)
            trace.append(public_url) if public_url!=-1 else trace.append(f'(Error) Cannot process : {str(table)}')
        except Exception as e:
            trace.append(f'(Error) Cannot process : {str(table)}')
    return trace


def web2md(soup, digest):
    text = str(soup).encode('utf-8')
    bytes_io = BytesIO(text)
    try:
        in_doc = InputDocument(
            path_or_stream=BytesIO(text),
            format=InputFormat.HTML,
            backend=HTMLDocumentBackend,
            filename=f"{digest}.html"
        )
        backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=bytes_io)
        dl_doc = backend.convert()
        md_data = dl_doc.export_to_markdown()
        return md_data
    except:
        return -1