import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.azure.document_intelligence import extract_figure_using_bbox
from utils.aws.s3 import get_s3_client, read_pdf_from_s3

load_dotenv()


url = 'https://sfopenaccessbucket.s3.us-east-1.amazonaws.com/uploads/9ad4054f-39b7-4e3b-8cb6-d99f3527bab2.pdf'

pdf_data = read_pdf_from_s3(get_s3_client(), url)
extract_figure_using_bbox(pdf_data, 11, [1.1235, 2.2592, 7.0518, 2.2594, 7.053, 7.2459, 1.1252, 7.245])