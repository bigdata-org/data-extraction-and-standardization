import streamlit as st
import requests
import json
from utils.helper import *

st.title('Welcome to Pytract-UI')
st.markdown('---')
st.subheader('Upload a PDF ')

if 'pdf_data' not in st.session_state:
    load_pdfs()

uploaded_file = st.file_uploader("Choose a file ", label_visibility="hidden")
submit_btn = st.button("Upload")

if submit_btn and uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        try:
            body = {"file":uploaded_file}
            response = requests.post(base_url+upload_object_endpoint,files=body)
            if response.status_code == 200 :
                st.success(f"PDF live @ {response.json()['url']}")
                load_pdfs()
            else :
                st.error(response.json()['detail'])
        except requests.exceptions.RequestException as e :
            st.error(e)
    else:
        st.warning(f"Input Document is not a PDF")
elif submit_btn and (uploaded_file is None) :
    st.warning(f"Choose a File to upload")     
    
# Display existing PDFs data in a table
if 'pdf_data' in st.session_state and not st.session_state['pdf_data'].empty:
    st.subheader("Existing PDFs:")
    st.dataframe(st.session_state['pdf_data'])
else:
    st.info("No existing PDFs found.")      

        