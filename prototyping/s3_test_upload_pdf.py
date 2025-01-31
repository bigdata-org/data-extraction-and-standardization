
# Test upload_pdf_to_s3

from io import BytesIO
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from utils.aws.s3 import get_s3_client, upload_pdf_to_s3

load_dotenv()
with open('C:\\Users\\sathy\\Downloads\\table_data.pdf',"rb") as f:
    bytes = f.read()
print(upload_pdf_to_s3(get_s3_client(), BytesIO(bytes)))



