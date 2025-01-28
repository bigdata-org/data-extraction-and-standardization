from firecrawl import FirecrawlApp
from utils.aws.s3 import write_markdown_to_s3
import hashlib

def get_firecrawl_client():
    return FirecrawlApp()

def scraper(s3_client, firecrawl_client, url):
    try:
        scrape_result = firecrawl_client.scrape_url(url, params={'formats': ['markdown']})
        md =  scrape_result['markdown']
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        endpoint = write_markdown_to_s3('firecrawl', s3_client, md, parent_file=url_hash)
        return endpoint
    except Exception as e:
        print(e)
        return -1
