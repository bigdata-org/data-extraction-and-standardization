import os
import boto3
from botocore.client import BaseClient
from uuid import uuid4
from io import BytesIO, StringIO
import pandas as pd

def get_s3_client():
    s3_client = boto3.client(
    's3', 
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")  
    )
    return s3_client

def read_pdf_from_s3(s3_client, url):
    bucket_name = os.getenv("BUCKET_NAME")
    if bucket_name is None :
        return -1
    url = url.split('/uploads/')
    if len(url)>1 and url[1].endswith('.pdf'):
        file_name = url[1]
        response = s3_client.get_object(Bucket=bucket_name, Key=f'uploads/{file_name}')
        return response["Body"].read()
    else :
        return -1
    
def upload_pdf_to_s3(s3_client, file_bytes_io: BytesIO):
    try:
        # Define S3 file path
        id = uuid4()
        s3_file_path = f"uploads/{id}.pdf"
        bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
        if bucket_name is None or aws_region is None:
            return -1
        # Upload the file to S3 using upload_fileobj
        s3_client.upload_fileobj(file_bytes_io, bucket_name, s3_file_path)

        # Construct the public URL for the uploaded file
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{s3_file_path}"

        return object_url
    except Exception as e:
        raise e
    
def write_dataframe_to_s3(s3_client, df: pd.DataFrame, parent_file='test', page=1):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    bucket_name = os.getenv("BUCKET_NAME")
    if bucket_name is None :
        return -1
    id = uuid4()
    try:
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{parent_file}/{page}/tables/'+str(id)+'.csv', Body=csv_buffer.getvalue())
    except Exception as e:
        print(e)
        
