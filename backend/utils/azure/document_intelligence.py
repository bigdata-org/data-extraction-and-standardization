import os
import fitz
import json
import pandas as pd  
import io
from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from utils.aws.s3 import write_image_to_s3, write_dataframe_to_s3, read_pdf_from_s3

def get_doc_int_client():
    endpoint = os.getenv("AZURE_DOC_INT_ENDPOINT")
    key = os.getenv("AZURE_DOC_INT_KEY")
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    return document_intelligence_client

# def extract_texts(poller_result):
#     return poller_result['content'] if 'content' in poller_result else None

def extracter(doc_int_client, s3_client, url):
    log=dict()
    poller = doc_int_client.begin_analyze_document(
    "prebuilt-layout",
    AnalyzeDocumentRequest(url_source=url),
    ) 
    data = poller.result()  
    #Process Figure
    pdf_raw_data = read_pdf_from_s3(s3_client, url)
    parent_file = url.split('/uploads/')[1].strip('.pdf')
    if 'figures' in data:
        f_trace = extract_figure(s3_client=s3_client, poller_result=data, parent_file=parent_file, pdf_raw_data = pdf_raw_data)
        log["figures"]=f_trace
    
    if 'tables' in data:       
        t_trace = extract_tables(s3_client=s3_client, poller_result=data, parent_file=parent_file)
        log["tables"]=t_trace
    return log

def extract_figure(s3_client, poller_result, parent_file, pdf_raw_data):
    trace=[]
    for d in poller_result['figures']:
        _p = d['id'].split('.')
        page_num, fig_num = int(_p[0]), int(_p[1])
        public_url = extract_figure_using_bbox(s3_client=s3_client,
                            pdf_data=pdf_raw_data,
                            parent_file=parent_file,
                            page_num=page_num,
                            id=fig_num,
                            polygon=d['boundingRegions'][0]['polygon']
                            )
        trace.append(public_url)
    return trace 

def extract_figure_using_bbox(s3_client, pdf_data, parent_file, page_num, id, polygon, dpi=72):
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    page = doc[page_num-1] #Zero based index
    
    pixmap = page.get_pixmap()
    w, h = pixmap.width, pixmap.height
    
    # Convert inch-based coordinates to pixels
    scaled_polygon = [(x * dpi, y * dpi) for x, y in zip(polygon[::2], polygon[1::2])]
    
    # Find the bounding box
    x_coords, y_coords = zip(*scaled_polygon)
    x1, y1 = int(min(x_coords)), int(min(y_coords))
    x2, y2 = int(max(x_coords)), int(max(y_coords))
    
    # Ensure coordinates are within the page bounds
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    
    # Extract the image data
    image = Image.frombytes("RGB", [w, h], pixmap.samples)
    
    # Crop the image
    cropped_image = image.crop((x1, y1, x2, y2))     # cropped_image.show()
    image_bytes_io = io.BytesIO()
    cropped_image.save(image_bytes_io, format="JPEG")   
    public_url = write_image_to_s3(
                            channel='azure-ai-document-intelligence', 
                            s3_client=s3_client, image_bytes=image_bytes_io.getvalue(), 
                            parent_file=parent_file, 
                            page_num=page_num, 
                            id=id
                        )
    doc.close()
    return public_url

def extract_tables(s3_client, poller_result, parent_file):
    trace=[]
    extract = lambda x: [i['content'] for i in x]
    t_index=dict()
    if 'tables' not in poller_result:
        return -1
    for table in poller_result['tables']:
        page_num = table['cells'][0]['boundingRegions'][0]['pageNumber'] 
        if page_num not in t_index:
            t_index[page_num]=1
        _table=[]       
        for _ in range(0,len(table['cells']), table['columnCount']):
            _table.append(extract(table['cells'][_ : _+table['columnCount']]))
        df = pd.DataFrame(_table[1:], columns=_table[0])
        public_url = write_dataframe_to_s3(
                                channel='azure-ai-document-intelligence', 
                                s3_client=s3_client,
                                df=df,
                                parent_file=parent_file,
                                page_num=page_num,
                                id=t_index[page_num]
                                )
        t_index[page_num] = t_index[page_num]+1
        trace.append(public_url)
    return trace

    
        
    