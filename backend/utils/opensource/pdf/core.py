import os
from pypdf import PdfReader
import pdfplumber
import pandas as pd
from docling.document_converter import DocumentConverter
from io import BytesIO, StringIO
from utils.aws.s3 import read_pdf_from_s3, write_image_to_s3, write_dataframe_to_s3


def extracter(s3_client, url):
    log={'images':[], 'tables':[]}
    image_trace = extract_unique_images_and_write_to_s3(s3_client, url)
    if image_trace!=-1:
        log['images']=image_trace
    table_trace = extract_tables_from_pdf(s3_client, url)
    if table_trace!=-1:
        log['tables']=table_trace
    return log
    
def extract_unique_images_and_write_to_s3(s3_client,url):
    trace = []
    parent_file = url.split('/uploads/')[1]
    pdf_bytes = read_pdf_from_s3(s3_client, url)
    pdf_bytes_io = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_bytes_io)
    try:
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            for id, image_file_object in enumerate(page.images):
                # image_data = BytesIO(image_file_object.data)
                image_bytes = image_file_object.data
                public_url = write_image_to_s3('opensource', s3_client, image_bytes, parent_file, page_number+1, id+1)
                trace.append(public_url) if public_url!=-1 else trace.append(f'(Error) Cannot process : {page}')
        return trace
    except Exception as e:
        print(e)
        return -1


def extract_tables_from_pdf(s3_client, url):
    trace = []
    parent_file = url.split('/uploads/')[1]
    try:
        pdf_bytes = read_pdf_from_s3(s3_client, url)
        pdf_bytes_io = BytesIO(pdf_bytes)
    except:
        return -1  # Return -1 if there is an issue reading the PDF from S3
    # Open the PDF file
    try:
        with pdfplumber.open(pdf_bytes_io) as pdf:
            try:
                file_counter=1
                for page_number, page in enumerate(pdf.pages):
                    # Extract table from the current page
                    table = page.extract_table()
                    if table:
                        # Convert the table into a DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])  # Skip the header row
                        # Save the DataFrame to a CSV file
                        if not df.empty:
                            # DF to in-memory csv
                            csv_buffer = StringIO()
                            df.to_csv(csv_buffer, index=False)
                            public_url =  write_dataframe_to_s3(channel='opensource', s3_client=s3_client, df=df, parent_file=parent_file, page_num=page_number+1, id=file_counter)
                            file_counter+=1
                            trace.append(public_url) if public_url!=-1 else trace.append(f'(Error) Cannot process : {page}')
            except:
                return -1
    except:
        return -1
    return trace   
    bucket_name = os.getenv('BUCKET_NAME')
    s3_client = s3.get_s3client()
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
    # Step 2: Convert HTML to Markdown using DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(html_file_path)
    markdown_content = result.document.export_to_markdown()

    # Step 3: Save Markdown content to file
    markdown_file_path = os.path.join(output_dir, "data_ex.md")
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return markdown_file_path