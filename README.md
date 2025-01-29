# Data Extraction and Standardization

This is a FastAPI-based web scraper that extracts images, tables, and metadata from a given URL using BeautifulSoup. The extracted data is then uploaded to an AWS S3 bucket, and a markdown file is generated containing links to the scraped content.

## Features
- Scrapes images, tables, and metadata from a given website.
- Saves extracted data into respective folders in an AWS S3 bucket.
- Standardizes extracted data before storage.
- Generates a markdown file with links to the extracted data.
- Provides a REST API to initiate web scraping.

## Technologies Used
- **FastAPI** - For building the REST API.
- **BeautifulSoup** - For web scraping.
- **boto3** - For interacting with AWS S3.
- **Pandas** - For processing HTML tables.
- **requests** - For handling HTTP requests.
- **dotenv** - For environment variable management.

## Installation



1. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add the following environment variables:
   ```env
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   S3_BUCKET_NAME=your_s3_bucket_name
   AWS_REGION=your_s3_region
   ```

## Usage

### Running the API

Run the FastAPI application with Uvicorn:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### **Root Endpoint**
- **GET /**
- **Response:**
  ```json
  {
    "message": "Web Scraper API - POST to /scrape with a URL"
  }
  ```

#### **Scrape Endpoint**
- **POST /scrape**
- **Request Body:**
  ```json
  {
    "url": "https://example.com"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "markdown_url": "s3_link_to_markdown_file",
    "metadata_url": "s3_link_to_metadata_file",
    "image_urls": ["s3_link_to_image1", "s3_link_to_image2"],
    "table_urls": ["s3_link_to_table1", "s3_link_to_table2"]
  }
  ```

## Project Structure
```
web-scraper-api/
│-- main.py          # FastAPI application
│-- requirements.txt # Required dependencies
│-- .env             # Environment variables
│-- README.md        # Project documentation
```





