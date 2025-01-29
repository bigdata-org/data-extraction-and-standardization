import os
from pypdf import PdfReader
import hashlib
from docling.document_converter import DocumentConverter
from io import BytesIO, StringIO
from utils.aws import s3
import uuid
from datetime import datetime
import pdfplumber
import pandas as pd 



def extract_unique_images_and_write_to_s3(s3_client,pdf, bucket_name, s3_prefix='pdf_images_extracted/'):
    reader = PdfReader(pdf)
    unique_hashes = set()
    try:
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            for count, image_file_object in enumerate(page.images):
               
                # Generate hash of image data
                image_hash = hashlib.md5(image_file_object.data).hexdigest()
                # Skip if duplicate
                if image_hash in unique_hashes:
                    continue
                # Add hash to unique set
                unique_hashes.add(image_hash)
               
                s3_storage = f"{s3_prefix}page_{page_number + 1}_image_{count + 1}.png"
                # Upload directly to S3 using BytesIO
                image_data = BytesIO(image_file_object.data)
                s3 = s3_client

                s3.upload_fileobj(
                    image_data,
                    bucket_name,
                    s3_storage
             )
        return {
                "status": "success"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def extract_tables_from_pdf(pdf_path,s3, bucket_name):
    # Ensure the output folder exists
    # os.makedirs(tables_folder, exist_ok=True)
    # bucket_name = os.getenv('BUCKET_NAME')
    bucket_name = bucket_name
    result = []
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        try:
            for page_number, page in enumerate(pdf.pages):
                # Extract table from the current page
                table = page.extract_table()
                if table:
                    # Convert the table into a DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])  # Skip the header row
                    # Save the DataFrame to a CSV file
                    if (not df.empty and  # Ensure the table isn't empty
                        df.apply(lambda x: x.str.strip().replace("", None)).notna().sum().sum() > 2  # Ensure non-empty content
                    ):
                        # DF to in-memory csv
                        csv_buffer = StringIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        s3_key = f"extracted_tables/table_number{page_number + 1}.csv"
                        s3_client = s3

                        s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=csv_buffer.getvalue()
                        )
                    result.append(f"Files successfully uploaded")
        except Exception as e :
            result.append(f"Error occured:{str(e)}")

    return result


def process_pdf_to_markdown(pdf_path):
   
    bucket_name = os.getenv('BUCKET_NAME')
    s3_client = s3.get_s3client()
    output_dir="temp_pdf_output"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Convert PDF to intermediate HTML
    reader = PdfReader(pdf_path)
    html_file_path = os.path.join(output_dir, "data_ex.html")

    with open(html_file_path, "w", encoding="utf-8") as fp:
        # Start HTML document structure
        fp.write("<!DOCTYPE html>\n")
        fp.write("<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n")
        fp.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        fp.write("<title>Extracted PDF Data</title>\n</head>\n<body>\n")

        # Extract text from PDF pages
        for page_number, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                fp.write("<p>\n")
                fp.write(page_text.replace("\n", "<br>\n"))
                fp.write("</p>\n")

        # End HTML document
        fp.write("</body>\n</html>\n")

    extract_unique_images_and_write_to_s3(s3_client,pdf_path, bucket_name,"pdf_images_extracted/")
    extract_tables_from_pdf(pdf_path, s3_client, bucket_name)
    # Step 2: Convert HTML to Markdown using DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(html_file_path)
    markdown_content = result.document.export_to_markdown()
    markdown_data = BytesIO(markdown_content.encode('utf-8'))
    s3_storage=f"generated_markdown/{datetime.now()}.md"
    
    s3_client.upload_fileobj(
        markdown_data,
        bucket_name,
        s3_storage
    )
    
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params= {'Bucket':bucket_name,'Key':s3_storage},
        ExpiresIn = 3600
    )
    # public_md_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_storage}"
    os.remove(html_file_path)
    
    return presigned_url