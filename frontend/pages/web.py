import streamlit as st
import requests
import pandas as pd

api_url = "http://127.0.0.1:8000"
list_object_endpoint = "/objects"
scrape_firecrawl_endpoint = "/scrape/firecrawl"
scrape_bs_endpoint = "/scrape/bs"


st.header("Enter Site URL")
url = st.text_input(label="Enter URL", label_visibility="hidden", placeholder="https://www.example.com")
tool_option = st.radio("Choose an option", ["Beautiful Soup", "Firecrawl"])
if st.button("Extract"):
    if url:
        endpoint = scrape_firecrawl_endpoint if tool_option=='Firecrawl' else scrape_bs_endpoint
        body = {"url":url}
        response = requests.post(api_url+endpoint, json=body)
        if response.status_code==200:
            result = response.json()
            if tool_option!='Firecrawl':
                img_df = pd.DataFrame(result['images'], columns=['images'])
                table_df = pd.DataFrame(result['tables'], columns=['tables'])
                st.subheader('Extracted Images')
                if img_df.shape[0]>0:
                    st.dataframe(img_df, hide_index=True)
                else:
                    st.warning('No Images Extracted')
                st.subheader('Extracted Tables')
                if table_df.shape[0]>0:
                    st.dataframe(table_df, hide_index=True)
                else:
                    st.warning('No Tables Extracted')                
            st.subheader('Markdown')
            st.markdown(result['md'])
        else:
            st.error('''
                    Cannot process this URL, it could be because of the following reasons:
                    - Invalid URL
                    - IP blacklist
                    - GET request to the site failed
                    - Error occurred in the extraction pipeline
                    ''') 
    else:
        st.error("Please enter a valid URL")