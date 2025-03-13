import socket
import streamlit as st
import requests
import pandas as pd

list_object_endpoint = "/objects"
upload_object_endpoint = "/upload"
base_url = 'http://localhost:8000'
extract_docint_endpoint = "/extract/doc-int"
extract_oss_endpoint = "/extract/opensource"
extract_docling_endpoint = "/extract/docling"
results_docint_endpoint = "/results/doc-int"
results_oss_endpoint = "/results/opensource"
results_docling_endpoint = "/results/docling"
summarize = "/text-summarize"
ask_question="/qa"

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def prettify_on(df, column):
    return df[df[column].apply(lambda x: '(Error)' not in x)]    

def load_pdfs():
    try:
        obj_res = requests.get(base_url + list_object_endpoint)
        if obj_res.status_code == 200:
            files = obj_res.json()
            if files:
                df = pd.DataFrame(files)
                df.rename(columns={
                    'file_name': 'File Name',
                    'file_size': 'Size (KB)',
                    'last_modified': 'Last Modified',
                    'url': 'Public Endpoint'
                }, inplace=True)
                st.session_state['pdf_data'] = df
            else:
                st.session_state['pdf_data'] = pd.DataFrame()
        else:
            st.error('We’re unable to retrieve the list of PDFs at the moment. Please try again later or contact support if the issue persists')
    except Exception as e:
        st.error(f'Server is down.. Error: {e}')        
            