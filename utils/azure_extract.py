import os
import fitz  
import json
from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

def get_doc_int_client():
    endpoint = os.getenv("AZURE_DOC_INT_ENDPOINT")
    key = os.getenv("AZURE_DOC_INT_KEY")
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    return document_intelligence_client

def extract_texts(poller_result):
    return poller_result['content'] if 'content' in poller_result else None

def extract_figures(poller_result):
    pass

def extract_tables(poller_result):
    pass

def extracter(doc_int_client, url):
        poller = doc_int_client.begin_analyze_document(
        "prebuilt-layout",
        AnalyzeDocumentRequest(url_source=url),
        )
        
        #Process Text

        #Process Image
        
        #Process Figure


##############################################


def extract_img_from_polygon(pdf_data, page_number, polygon, dpi=72):
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    page = doc[page_number-1] #Zero based index
    
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
    cropped_image = image.crop((x1, y1, x2, y2))
    
    cropped_image.show()
    
    doc.close()
    return cropped_image


    
        
    