import base64
from pathlib import Path
from io import BytesIO
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream
from docling_core.types.doc import ImageRefMode
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from backend.utils.aws.s3 import get_s3_client, read_pdf_from_s3, write_image_to_s3_nopage, write_markdown_to_s3


def PDF2MD(s3_client, url):
    parent_file = url.split('/uploads/')[1]
    local_filepath = save_b64_markdown(url, parent_file)
    if not isinstance(local_filepath, int):
        markdown = process_markdown(s3_client, local_filepath)
        if not isinstance(markdown, int):
            object_url = write_markdown_to_s3('docling', s3_client, markdown, parent_file)
        else:
            return markdown #return error code (either -3 or -4)
    else:
        return local_filepath #return error code (either -1 or -2)
    return object_url   

def save_b64_markdown(url, parent_file):
    try:
        pdf_data = read_pdf_from_s3(get_s3_client(), url)
    except:
        return -1
    try:
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
        output_dir=Path('backend/artifacts/docling')
        output_dir.mkdir(parents=True, exist_ok=True)
        parent_file = conv_res.input.file.stem
        md_filepath = output_dir / f"{parent_file}.md"
        conv_res.document.save_as_markdown(md_filepath, image_mode=ImageRefMode.EMBEDDED)
        return md_filepath
    except:
        return -2

def process_markdown(s3_client, local_filepath):
    try:
        with open(local_filepath, 'rb') as f:
            _md = f.read().decode('utf-8')  #str object
    except:
        return -3
    try:
        _md = _md.replace("\r\n", "\n").replace("\r", "\n")
        _md_lst = _md.split("\n")
        for i,d in enumerate(_md_lst):
            if '![Image]' in d:
                base64_string = _md_lst[i].split('![Image](data:')[1].split(',')[1]
                image_bytes = base64.b64decode(base64_string)
                object_url = write_image_to_s3_nopage('docling', s3_client, image_bytes, parent_file=local_filepath.stem, id=i+1)
                _md_lst[i] = f'![Image]({object_url})'
        md = "\n".join(_md_lst)
        return md
    except:
        return -4