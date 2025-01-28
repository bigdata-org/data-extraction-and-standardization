from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os 
from utils.convert_pdf import process_pdf_to_markdown

# Create a FastAPI application
app = FastAPI(docs_url="/docs")

    
@app.post("/pdfToMd-text/")
async def convert_pdf_to_md(file: UploadFile = File(...)):

    # Save the uploaded file temporarily
    input_pdf_path = f"temp_{file.filename}"
    with open(input_pdf_path, "wb") as f:
        f.write(await file.read())
    # Process the PDF to Markdown
    markdown_file_path = process_pdf_to_markdown(input_pdf_path)

    # Remove the temporary input PDF file
    os.remove(input_pdf_path)
    
    # Return the Markdown file as a response
    return FileResponse(markdown_file_path, media_type="text/markdown", filename="data_ex.md")
