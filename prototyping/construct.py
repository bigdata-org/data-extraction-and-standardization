# def save_text_and_tables(document, output_dir):
#     markdown_content = document.export_to_markdown()
#     with open(os.path.join(output_dir, 'text_and_tables.md'), 'w', encoding='utf-8') as f:
#         f.write(markdown_content)
#     print(f"Text and tables saved to: {os.path.join(output_dir, 'text_and_tables.md')}")
import sys
import os
import json
from pathlib import Path
import pandas as pd
from io import BytesIO
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from docling_core.types.doc import ImageRefMode
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from utils.aws.s3 import get_s3_client, read_pdf_from_s3

url = "https://sfopenaccessbucket.s3.us-east-1.amazonaws.com/uploads/649af4f1-a280-43b3-8135-1664e7db178b.pdf"
parent_file = url.split('/uploads/')[1]
pdf_data = read_pdf_from_s3(get_s3_client(),url )
buf = BytesIO(pdf_data)
source = DocumentStream(name=parent_file, stream=buf)
IMAGE_RESOLUTION_SCALE = 2.0
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
conv_res = converter.convert(source)
picture_counter=0
output_dir=Path('artifacts/docling')
output_dir.mkdir(parents=True, exist_ok=True)
doc_filename = conv_res.input.file.stem

md_filename = output_dir / f"{doc_filename}.md"
conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)
# conv_res.document.export_to_markdown()


