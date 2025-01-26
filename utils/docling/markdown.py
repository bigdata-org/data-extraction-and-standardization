import sys
import os
import json
import base64
from pathlib import Path
import pandas as pd
from io import BytesIO
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from docling_core.types.doc import ImageRefMode
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from utils.aws.s3 import get_s3_client, read_pdf_from_s3, write_image_to_s3, write_image_to_s3_nopage, write_markdown_to_s3


def PDF2MD(s3_client, url):
    parent_file = url.split('/uploads/')[1]
    local_filepath = save_b64_markdown(url, parent_file)
    markdown = process_markdown(s3_client, local_filepath)
    object_url = write_markdown_to_s3('docling', s3_client, markdown, parent_file)
    return object_url   

def save_b64_markdown(url, parent_file):
    pdf_data = read_pdf_from_s3(get_s3_client(), url)
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
    output_dir=Path('artifacts/docling')
    output_dir.mkdir(parents=True, exist_ok=True)
    parent_file = conv_res.input.file.stem
    md_filepath = output_dir / f"{parent_file}.md"
    conv_res.document.save_as_markdown(md_filepath, image_mode=ImageRefMode.EMBEDDED)
    return md_filepath

def process_markdown(s3_client, local_filepath):
    with open(local_filepath, 'rb') as f:
        _md = f.read().decode('utf-8')  #str object
    _md_lst = _md.split("\n")
    for i,d in enumerate(_md_lst):
        if '![Image]' in d:
            base64_string = _md_lst[i].split('![Image](data:')[1].split(',')[1]
            image_bytes = base64.b64decode(base64_string)
            object_url = write_image_to_s3_nopage('docling', s3_client, image_bytes, parent_file=local_filepath.stem)
            _md_lst[i] = f'![Image]({object_url})'
    md = "\n".join(_md_lst)
    return md