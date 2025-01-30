

# Final update in the code

import streamlit as st
import requests

def fetch_markdown_content(markdown_url: str) -> str:
    try:
        response = requests.get(markdown_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Failed to fetch markdown from S3: {e}")
        return ""

def main():
    st.title("Web Scraper Frontend")

    url_input = st.text_input("Enter URL to scrape")

    engine = st.selectbox(
        "Select Scraping Engine",
        ("BeautifulSoup", "FireCrawl")
    )

    if st.button("Scrape"):
        if not url_input:
            st.warning("Please enter a valid URL.")
            return

        if engine == "BeautifulSoup":
            try:
                scrape_api_url = "http://localhost:8000/scrape"  # endpoint for scraper
                payload = {"url": url_input}
                response = requests.post(scrape_api_url, json=payload)
                response.raise_for_status()
                result = response.json()

                markdown_url = result.get("markdown_url")
                if markdown_url:
                    # Fetch the consolidated Markdown from S3
                    markdown_content = fetch_markdown_content(markdown_url)
                    if markdown_content:
                        # Render the entire scraped data
                        st.markdown(markdown_content)
                else:
                    st.error("No markdown_url returned from the API.")
            except requests.exceptions.RequestException as e:
                st.error(f"Request to backend failed: {e}")
        else:
            st.info("FireCrawl functionality will be implemented later.")

if __name__ == "__main__":
    main()
