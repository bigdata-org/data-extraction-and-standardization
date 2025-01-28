from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os 
from utils import convert_pdf, docling_conversion

# Create a FastAPI application
app = FastAPI(docs_url="/docs")

    
@app.post("/pdfToMd-text/")
async def convert_pdf_to_md(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    input_pdf_path = f"temp_{file.filename}"
    with open(input_pdf_path, "wb") as f:
        f.write(await file.read())
    # Process the PDF to Markdown
    markdown_file_path = convert_pdf.process_pdf_to_markdown(input_pdf_path)
    # Remove the temporary input PDF file
    os.remove(input_pdf_path)
    # Return the Markdown file as a response
    return FileResponse(markdown_file_path, media_type="text/markdown", filename="OpenSourceConversion.md")

@app.post("/pdfToMd_docling/")
async def pdfTOMd_conversion_docling(file: UploadFile = File()):
    input_pdf_path = f"temp_{file.filename}"
    with open(input_pdf_path,"wb") as fp:
        fp.write(await file.read())
    md_file_path = docling_conversion.pdf_to_md_docling(input_pdf_path)
    os.remove(input_pdf_path)
    return FileResponse(md_file_path, media_type="text/markdown", filename="doclingConversion.md")
