import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from utils.aws.s3 import get_s3_client, write_image_to_s3
# image_path = 'C:\\Users\\sathy\\Desktop\\linkedin.jpg'
image_path = 'C:\\Users\\sathy\\Pictures\\Screenshots\\Screenshot 2024-09-09 223201.png'
with open(image_path,'rb') as f:
    image_bytes = f.read()

write_image_to_s3(get_s3_client(), image_bytes)