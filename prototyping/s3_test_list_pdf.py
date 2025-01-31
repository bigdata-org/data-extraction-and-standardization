import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from backend.utils.aws.s3 import get_s3_client, list_pdfs_from_s3

print(list_pdfs_from_s3(get_s3_client(), container_name='uploads'))
