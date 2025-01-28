import os
from pypdf import PdfReader
from pypdf import PdfReader
import hashlib
from docling.document_converter import DocumentConverter


def extract_unique_images_from_pdf(pdf):
    images_folder = "extracted_images"
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    reader = PdfReader(pdf)
    unique_hashes = set()

    for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        for count, image_file_object in enumerate(page.images):
            image_hash = hashlib.md5(image_file_object.data).hexdigest()
            if image_hash in unique_hashes:
                continue
            # Add hash to unique set and save image
            unique_hashes.add(image_hash)
            temp_image_file_path = os.path.join(images_folder, f"page_{page_number + 1}_image_{count + 1}.png")
            # //temp_image_file_path = f"temp_{file.filename}"
            with open(temp_image_file_path, "wb") as img_fp:
                img_fp.write(image_file_object.data)
    

    return temp_image_file_path


def process_pdf_to_markdown(pdf_path, output_dir="pdf_output"):
   
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

    # Step 2: Convert HTML to Markdown using DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(html_file_path)
    markdown_content = result.document.export_to_markdown()

    # Step 3: Save Markdown content to file
    markdown_file_path = os.path.join(output_dir, "data_ex.md")
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    return markdown_file_path