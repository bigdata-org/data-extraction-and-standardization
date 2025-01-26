import os
import boto3
import fitz
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
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=f'uploads/{file_name}')
            pdf_bytes =  response["Body"].read()
            return pdf_bytes
        except Exception as e:
            print(e)
            return -1
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
    
def write_dataframe_to_s3(channel, s3_client, df: pd.DataFrame, parent_file, page_num, id):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/{page_num}/tables/{id}.csv', Body=csv_buffer.getvalue())
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/{page_num}/tables/{id}.csv"
        return object_url
    except Exception as e:
        print(e)
        
def write_markdown_to_s3(channel, s3_client, md, parent_file):    
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/content.md', Body=md)
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/content.md"
        return object_url
    except Exception as e:
        print(e)    
        
def write_image_to_s3(channel, s3_client, image_bytes, parent_file, page_num, id):    
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/{page_num}/images/{id}.jpeg', Body=image_bytes)
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/{page_num}/images/{id}.jpeg"
        return object_url
    except Exception as e:
        print(e)
        
def write_image_to_s3_nopage(channel, s3_client, image_bytes, parent_file):    
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        id=uuid4()
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/images/{id}.jpeg', Body=image_bytes)
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/images/{id}.jpeg"
        return object_url
    except Exception as e:
        print(e)   
