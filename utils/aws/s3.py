import boto3
from dotenv import load_dotenv
import os


# load_dotenv()
def get_s3client():
    s3 = boto3.client(
        's3',
        aws_access_key_id= os.getenv("ACCESS_KEY"),
        aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
        region_name = os.getenv('REGION')
    )
    return s3



    