
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os
# import requests
# import boto3
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pandas as pd
# import json
# from io import StringIO
# from typing import List
# from dotenv import load_dotenv

# app = FastAPI()


# load_dotenv()

# AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
# S3_REGION = os.getenv('AWS_REGION')

# class ScrapeRequest(BaseModel):
#     url: str

# def upload_to_s3(file_path: str, s3_key: str) -> str:
#     s3 = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY,
#         region_name=S3_REGION
#     )
#     try:
#         s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)
#         s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
#         return s3_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"S3 Upload Error: {str(e)}")

# def scrape_images(url: str) -> List[str]:
#     try:
#         save_directory = "images"
#         os.makedirs(save_directory, exist_ok=True)
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         img_tags = soup.find_all('img')
#         image_urls = []
        
#         for img_tag in img_tags:
#             img_url = img_tag.get('src')
#             if img_url:
#                 img_url = urljoin(url, img_url)
#                 img_name = os.path.basename(img_url)
#                 img_path = os.path.join(save_directory, img_name)
#                 try:
#                     img_data = requests.get(img_url).content
#                     with open(img_path, 'wb') as img_file:
#                         img_file.write(img_data)
                    
#                     s3_key = f"scraped_images/{img_name}"
#                     s3_url = upload_to_s3(img_path, s3_key)
#                     image_urls.append(s3_url)
#                 except Exception as e:
#                     print(f"Failed to process image {img_url}: {str(e)}")
#         return image_urls
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Image Scraping Error: {str(e)}")

# def scrape_tables(url: str) -> List[str]:
#     try:
#         output_directory = "tables"
#         os.makedirs(output_directory, exist_ok=True)
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         tables = soup.find_all('table')
#         table_files = []
        
#         for i, table in enumerate(tables):
#             try:
#                 df = pd.read_html(StringIO(str(table)))[0]
#                 file_path = os.path.join(output_directory, f"table_{i + 1}.csv")
#                 df.to_csv(file_path, index=False)
                
#                 # Upload to S3
#                 s3_key = f"tables/table_{i + 1}.csv"
#                 s3_url = upload_to_s3(file_path, s3_key)
#                 table_files.append(s3_url)
#             except Exception as e:
#                 print(f"Failed to process table {i + 1}: {str(e)}")
#         return table_files
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Table Scraping Error: {str(e)}")

# def scrape_metadata(url: str) -> str:
#     try:
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         metadata = {
#             "title": soup.title.string if soup.title else "No Title",
#             "meta_tags": [
#                 {"name": tag.get("name"), "content": tag.get("content")}
#                 for tag in soup.find_all("meta")
#             ]
#         }
        
#         metadata_file = "metadata.json"
#         with open(metadata_file, "w", encoding="utf-8") as file:
#             json.dump(metadata, file, indent=4)
        
#         s3_key = f"metadata/{os.path.basename(metadata_file)}"
#         s3_url = upload_to_s3(metadata_file, s3_key)
#         return s3_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Metadata Scraping Error: {str(e)}")

# def create_markdown(metadata_url: str, table_urls: List[str], image_urls: List[str]) -> str:
#     try:
#         # Generate markdown content
#         markdown_content = "# Scraped Data\n\n"
        
#         # Add Metadata
#         markdown_content += "## Metadata\n"
#         markdown_content += f"[View Metadata]({metadata_url})\n\n"
        
#         # Add Images
#         markdown_content += "## Images\n"
#         for img_url in image_urls:
#             markdown_content += f"![Image]({img_url})\n"
        
#         # Add Tables
#         markdown_content += "## Tables\n"
#         for table_url in table_urls:
#             markdown_content += f"[View Table]({table_url})\n"
        
#         # Save and upload markdown
#         markdown_file = "scraped_data.md"
#         with open(markdown_file, "w", encoding="utf-8") as file:
#             file.write(markdown_content)
        
#         s3_key = f"markdown/{markdown_file}"
#         markdown_url = upload_to_s3(markdown_file, s3_key)
#         return markdown_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Markdown Generation Error: {str(e)}")


# # API for web scraping

# #url = "https://www.geeksforgeeks.org/python-programming-language-tutorial/"

# @app.post("/scrape")
# async def scrape_website(request: ScrapeRequest):
#     try:
#         if not request.url.startswith(('http://', 'https://')):
#             raise HTTPException(status_code=400, detail="Invalid URL format")
        
#         image_urls = scrape_images(request.url)
#         table_urls = scrape_tables(request.url)
#         metadata_url = scrape_metadata(request.url)
#         markdown_url = create_markdown(metadata_url, table_urls, image_urls)
        
#         return {
#             "status": "success",
#             "markdown_url": markdown_url,
#             "metadata_url": metadata_url,
#             "image_urls": image_urls,
#             "table_urls": table_urls
#         }
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# @app.get("/")
# def read_root():
#     return {"message": "Web Scraper API - POST to /scrape with a URL"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)







# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os
# import requests
# import boto3
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import pandas as pd
# import json
# from io import StringIO
# from typing import List
# from dotenv import load_dotenv

# load_dotenv()

# AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
# S3_REGION = os.getenv('AWS_REGION')

# if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET_NAME, S3_REGION]):
#     raise RuntimeError("Missing required S3-related environment variables.")

# app = FastAPI()

# class ScrapeRequest(BaseModel):
#     url: str

# def upload_to_s3(file_path: str, s3_key: str) -> str:
#     s3 = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY,
#         region_name=S3_REGION
#     )
#     try:
#         s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)
#         s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
#         return s3_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"S3 Upload Error: {str(e)}")

# def scrape_images(url: str) -> List[str]:
#     try:
#         save_directory = "images"
#         os.makedirs(save_directory, exist_ok=True)
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         img_tags = soup.find_all('img')
#         image_urls = []
        
#         for img_tag in img_tags:
#             img_url = img_tag.get('src')
#             if img_url:
#                 img_url = urljoin(url, img_url)
#                 img_name = os.path.basename(img_url)
#                 img_path = os.path.join(save_directory, img_name)
#                 try:
#                     img_data = requests.get(img_url).content
#                     with open(img_path, 'wb') as img_file:
#                         img_file.write(img_data)
                    
#                     s3_key = f"scraped_images/{img_name}"
#                     s3_url = upload_to_s3(img_path, s3_key)
#                     image_urls.append(s3_url)
#                 except Exception as e:
#                     print(f"Failed to process image {img_url}: {str(e)}")
#         return image_urls
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Image Scraping Error: {str(e)}")

# def scrape_tables(url: str) -> List[str]:
#     try:
#         output_directory = "tables"
#         os.makedirs(output_directory, exist_ok=True)
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         tables = soup.find_all('table')
#         table_files = []
        
#         for i, table in enumerate(tables):
#             try:
#                 df = pd.read_html(StringIO(str(table)))[0]
#                 file_path = os.path.join(output_directory, f"table_{i + 1}.csv")
#                 df.to_csv(file_path, index=False)
                
#                 s3_key = f"tables/table_{i + 1}.csv"
#                 s3_url = upload_to_s3(file_path, s3_key)
#                 table_files.append(s3_url)
#             except Exception as e:
#                 print(f"Failed to process table {i + 1}: {str(e)}")
#         return table_files
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Table Scraping Error: {str(e)}")

# def scrape_metadata(url: str) -> str:
#     try:
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         metadata = {
#             "title": soup.title.string if soup.title else "No Title",
#             "meta_tags": [
#                 {"name": tag.get("name"), "content": tag.get("content")}
#                 for tag in soup.find_all("meta")
#             ]
#         }
        
#         metadata_file = "metadata.json"
#         with open(metadata_file, "w", encoding="utf-8") as file:
#             json.dump(metadata, file, indent=4)
        
#         s3_key = f"metadata/{os.path.basename(metadata_file)}"
#         s3_url = upload_to_s3(metadata_file, s3_key)
#         return s3_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Metadata Scraping Error: {str(e)}")

# def create_markdown(metadata_url: str, table_urls: List[str], image_urls: List[str]) -> str:
#     try:
#         markdown_content = "# Scraped Data\n"

#         # Embed metadata JSON in Markdown
#         markdown_content += "\n## Metadata\n"
#         try:
#             meta_resp = requests.get(metadata_url)
#             meta_resp.raise_for_status()
#             metadata_json = meta_resp.json()
#             metadata_str = json.dumps(metadata_json, indent=4)
#             markdown_content += f"``````\n"
#         except Exception as e:
#             markdown_content += f"Failed to inline metadata from {metadata_url}: {e}\n"

#         # Inline images
#         markdown_content += "\n## Images\n"
#         for img_url in image_urls:
#             markdown_content += f"![Scraped Image]({img_url})\n"

#         # Embed tables as Markdown
#         markdown_content += "\n## Tables\n"
#         for i, table_url in enumerate(table_urls, start=1):
#             try:
#                 table_resp = requests.get(table_url)
#                 table_resp.raise_for_status()
#                 df = pd.read_csv(StringIO(table_resp.text))
#                 md_table = df.to_markdown(index=False)
#                 markdown_content += f"\n### Table {i}\n\n{md_table}\n"
#             except Exception as e:
#                 markdown_content += f"\nFailed to embed table {i} from {table_url}: {e}\n"

#         markdown_file = "scraped_data.md"
#         with open(markdown_file, "w", encoding="utf-8") as file:
#             file.write(markdown_content)

#         s3_key = f"markdown/{markdown_file}"
#         markdown_url = upload_to_s3(markdown_file, s3_key)
#         return markdown_url
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Markdown Generation Error: {str(e)}")

# @app.post("/scrape")
# async def scrape_website(request: ScrapeRequest):
#     try:
#         if not request.url.startswith(('http://', 'https://')):
#             raise HTTPException(status_code=400, detail="Invalid URL format")
        
#         image_urls = scrape_images(request.url)
#         table_urls = scrape_tables(request.url)
#         metadata_url = scrape_metadata(request.url)
#         markdown_url = create_markdown(metadata_url, table_urls, image_urls)
        
#         return {
#             "status": "success",
#             "markdown_url": markdown_url,
#             "metadata_url": metadata_url,
#             "image_urls": image_urls,
#             "table_urls": table_urls
#         }
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# @app.get("/")
# def read_root():
#     return {"message": "Web Scraper API - POST to /scrape with a URL"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)






#Final changes for FASTAPI

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import json
from io import StringIO
from typing import List
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('AWS_REGION')

if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, S3_BUCKET_NAME, S3_REGION]):
    raise RuntimeError("Missing required S3-related environment variables.")

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

def upload_to_s3(file_path: str, s3_key: str) -> str:
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=S3_REGION
    )
    try:
        s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        return f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload Error: {str(e)}")

def scrape_images(url: str) -> List[str]:
    try:
        save_directory = "images"
        os.makedirs(save_directory, exist_ok=True)

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        img_tags = soup.find_all('img')
        image_urls = []

        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if img_url:
                img_url = urljoin(url, img_url)
                img_name = os.path.basename(img_url)
                img_path = os.path.join(save_directory, img_name)
                try:
                    img_data = requests.get(img_url).content
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_data)

                    s3_key = f"scraped_images/{img_name}"
                    s3_url = upload_to_s3(img_path, s3_key)
                    image_urls.append(s3_url)
                except Exception as e:
                    print(f"Failed to process image {img_url}: {e}")
        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image Scraping Error: {str(e)}")

def scrape_tables(url: str) -> List[str]:
    try:
        output_directory = "tables"
        os.makedirs(output_directory, exist_ok=True)

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all('table')
        table_files = []

        for i, table_html in enumerate(tables, start=1):
            try:
                df = pd.read_html(StringIO(str(table_html)))[0]
                file_path = os.path.join(output_directory, f"table_{i}.csv")
                df.to_csv(file_path, index=False)

                s3_key = f"tables/table_{i}.csv"
                s3_url = upload_to_s3(file_path, s3_key)
                table_files.append(s3_url)
            except Exception as e:
                print(f"Failed to process table {i}: {e}")
        return table_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table Scraping Error: {str(e)}")

def scrape_metadata(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        metadata = {
            "title": soup.title.string if soup.title else "No Title",
            "meta_tags": [
                {"name": tag.get("name"), "content": tag.get("content")}
                for tag in soup.find_all("meta")
            ]
        }

        metadata_file = "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)

        s3_key = f"metadata/{os.path.basename(metadata_file)}"
        s3_url = upload_to_s3(metadata_file, s3_key)
        return s3_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metadata Scraping Error: {str(e)}")

def create_markdown(metadata_url: str, table_urls: List[str], image_urls: List[str]) -> str:
    """
    Generate one consolidated Markdown file embedding metadata (as JSON),
    displaying images inline, and rendering tables as Markdown.
    """
    try:
        markdown_content = "# Scraped Data\n"

        # 1) Embed Metadata JSON
        markdown_content += "\n## Metadata\n"
        try:
            meta_resp = requests.get(metadata_url)
            meta_resp.raise_for_status()
            metadata_json = meta_resp.json()

            # Convert JSON to a prettified string
            metadata_str = json.dumps(metadata_json, indent=4)

            # Put JSON in a code fence
            # This automatically shows the JSON inside the final Markdown
            markdown_content += "```"
            markdown_content += metadata_str
            markdown_content += "\n```\n"
        except Exception as e:
            markdown_content += f"Failed to inline metadata from {metadata_url}: {e}\n"

        # 2) Inline images
        markdown_content += "\n## Images\n"
        for img_url in image_urls:
            # This syntax displays the image inline in Markdown
            markdown_content += f"![Scraped Image]({img_url})\n\n"

        # 3) Embed tables as Markdown
        markdown_content += "\n## Tables\n"
        for i, table_url in enumerate(table_urls, start=1):
            try:
                table_resp = requests.get(table_url)
                table_resp.raise_for_status()

                df = pd.read_csv(StringIO(table_resp.text))
                # Convert DataFrame into a Markdown table
                md_table = df.to_markdown(index=False)

                markdown_content += f"\n### Table {i}\n\n{md_table}\n"
            except Exception as e:
                markdown_content += f"\nFailed to embed table {i} from {table_url}: {e}\n"

        # Save the final Markdown to a local file
        markdown_file = "scraped_data.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Upload the final Markdown to S3
        s3_key = f"markdown/{markdown_file}"
        markdown_url = upload_to_s3(markdown_file, s3_key)
        return markdown_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown Generation Error: {str(e)}")


@app.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    """
    Scrapes the website for metadata, tables, images, then merges all
    into one final Markdown file that references everything inline.
    """
    try:
        if not request.url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # 1) Scrape Images -> s3 URLs
        image_urls = scrape_images(request.url)

        # 2) Scrape Tables -> s3 CSV URLs
        table_urls = scrape_tables(request.url)

        # 3) Scrape Metadata -> s3 JSON URL
        metadata_url = scrape_metadata(request.url)

        # 4) Combine everything into a single Markdown file, then upload
        markdown_url = create_markdown(metadata_url, table_urls, image_urls)

        return {
            "status": "success",
            "markdown_url": markdown_url,
            "metadata_url": metadata_url,
            "image_urls": image_urls,
            "table_urls": table_urls
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "Web Scraper API - POST to /scrape with a URL"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
