import os
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
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
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    url = url.split('/uploads/')
    if len(url)>1 and url[1].endswith('.pdf'):
        file_name = url[1]
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=f'uploads/{file_name}')
            pdf_bytes =  response["Body"].read()
            endpoint = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/uploads/{id}.pdf"            
            return pdf_bytes, endpoint
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchKey":
                print("Error: The specified file does not exist.")
            else:
                print(f"ClientError: {e}")
            return -1
        except EndpointConnectionError as e:
            print("Error: Could not connect to the S3 endpoint. Check your configuration.")
            return -2
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return -999
    else :
        return -3
    
def read_markdown_from_s3(s3_client, file_name):
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=f'results/docling/{file_name}/content.md')
        markdown_content = response["Body"].read()  # Decode bytes to string .decode("utf-8")
        endpoint = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/docling/{file_name}/content.md"            
        return markdown_content, endpoint
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            print("Error: The specified file does not exist.")
        else:
            print(f"ClientError: {e}")
        return -1
    except EndpointConnectionError as e:
        print("Error: Could not connect to the S3 endpoint. Check your configuration.")
        return -2
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return -999
    
def upload_pdf_to_s3(s3_client, file_bytes_io: BytesIO):
    try:
        bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
        if bucket_name is None or aws_region is None:
            return -1
        # Define S3 file path
        id = uuid4()
        s3_file_path = f"uploads/{id}.pdf"
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
        parent_file = parent_file.strip('.pdf')
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
        parent_file = parent_file.strip('.pdf')
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/content.md', Body=md.encode('utf-8'), ContentType='text/markdown')
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/content.md"
        return object_url
    except Exception as e:
        print(e)
        return -1    
        
def write_image_to_s3(channel, s3_client, image_bytes, parent_file, page_num, id):    
    bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
    if bucket_name is None or aws_region is None:
        return -1
    try:
        parent_file = parent_file.strip('.pdf')
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
        parent_file = parent_file.strip('.pdf')
        id=uuid4()
        s3_client.put_object(Bucket=bucket_name, Key=f'results/{channel}/{parent_file}/images/{id}.jpeg', Body=image_bytes)
        object_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/results/{channel}/{parent_file}/images/{id}.jpeg"
        return object_url
    except Exception as e:
        print(e)
        
def list_pdfs_from_s3(s3_client, container_name):
    """
    List all PDFs in a specific container (prefix) in the S3 bucket.

    :param s3_client: Boto3 S3 client
    :param container_name: Name of the container (prefix) to filter objects
    :return: List of PDF details (file_name, file_size, last_modified)
    """
    try:
        bucket_name, aws_region = os.getenv("BUCKET_NAME"), os.getenv('AWS_REGION')
        if bucket_name is None or aws_region is None:
            return -1
        
        pdf_details = []
        prefix = f"{container_name}/"  # Set the prefix based on the container name

        # Paginate through the S3 bucket to list objects with the specified prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        response_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        for page in response_iterator:
            if "Contents" in page:
                for obj in page["Contents"]:
                    key = obj["Key"]
                    filename = key.split("/")[-1]
                    if key.endswith(".pdf"):  # Check if the file is a PDF
                        size_kb = round(obj["Size"] / 1024)
                        last_modified = obj["LastModified"]
                        # Format the date as a readable string
                        last_modified_str = last_modified.strftime("%Y-%m-%d %H:%M:%S")
                        public_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{key}"
                        pdf_details.append({
                            "file_name": filename,
                            "file_size": size_kb,
                            "last_modified": last_modified_str,
                            "url" : public_url
                        })
        
        return pdf_details
    except Exception as e:
        print(f"Error listing PDFs: {e}")
        return []   
   
