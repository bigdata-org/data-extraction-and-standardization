import streamlit as st
import requests
import pandas as pd
from utils.helper import prettify_on

st.title('Pytract-WEB Core')
st.markdown('---')
api_url = "http://127.0.0.1:8000"
scrape_firecrawl_endpoint = "/scrape/firecrawl"
scrape_bs_endpoint = "/scrape/bs"

def clear_session_state():
    st.session_state.result = None
    
st.header("Enter Site URL")
url = st.text_input(label="Enter URL", label_visibility="hidden", placeholder="https://www.example.com")
tool_option = st.radio("Choose an option", ["Beautiful Soup", "Firecrawl"], on_change=clear_session_state)

if 'result' not in st.session_state:  # Initialize result if not in session_state
    st.session_state.result = None
    
if st.button("Extract"):
    if url:
        endpoint = scrape_firecrawl_endpoint if tool_option == 'Firecrawl' else scrape_bs_endpoint
        body = {"url": url}
        response = requests.post(api_url + endpoint, json=body)
        
        if response.status_code == 200:
            st.session_state.result = response.json()  # Store response in session_state
        else:
            st.error(
                "Cannot process this URL, it could be because of the following reasons:\n\n"
                "- **Invalid URL**\n"
                "- **IP blacklist**\n"
                "- **GET request to the site failed**\n"
                "- **Error occurred in the extraction pipeline**"
            )
    else:
        st.error("Please enter a valid URL")

# Check if result is in session_state and display accordingly
if st.session_state.result:
    result = st.session_state.result
    if tool_option != 'Firecrawl':
        img_df = pd.DataFrame(result['images'], columns=['images'])
        table_df = pd.DataFrame(result['tables'], columns=['tables'])
        
        st.subheader('Extracted Images')
        if img_df.shape[0] > 0:
            if st.checkbox('Prettify', key='prettify_images'):
                img_df = prettify_on(img_df, 'images')
                if img_df.shape[0] > 0:
                    st.dataframe(img_df, hide_index=True, use_container_width=True)
                else:
                    st.warning('Most of the images on the website are stored statically, so they cannot be accessed over HTTPS')
            else:
                st.dataframe(img_df, hide_index=True, use_container_width=True)
        else:
            st.warning('No Images Extracted')

        st.subheader('Extracted Tables')
        if table_df.shape[0] > 0:
            if st.checkbox('Prettify', key='prettify_tables'):
                table_df = prettify_on(table_df, 'tables')  # Replace 'tables' with the correct column name if needed
                if table_df.shape[0] > 0:
                    st.dataframe(table_df, hide_index=True, use_container_width=True)
                else:
                    st.warning('Some of the tables might have static content that cannot be processed over HTTPS')
            else:
                st.dataframe(table_df, hide_index=True, use_container_width=True)
        else:
            st.warning('No Tables Extracted')
        st.subheader('Markdown')
        st.markdown(result['md'])
    else:
        st.subheader('Markdown')
        st.markdown(result['md'])        