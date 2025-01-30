import streamlit as st
import requests
import pandas as pd 

st.title('Welcome to the App!')


# Test code for markdown rendering --works 
# file_name = '649af4f1-a280-43b3-8135-1664e7db178b'
# api_url = f"http://localhost:8000/results/docling/{file_name}"  # Replace with your FastAPI endpoint

# response = requests.get(api_url)
# res = response.json()
# st.markdown(res["markdown"])



document_type_selectBox = st.sidebar.selectbox(
    'Select document type',('PDF','WebUrl')
)

add_selectBox =  st.sidebar.selectbox(
    'Select tool for conversion',
    ('OpenSource', 'Enterprise', 'Docling')
)

uploaded_file = st.file_uploader("Choose a file ")

if document_type_selectBox == 'PDF' and add_selectBox == 'OpenSource' and uploaded_file is not None:
    api_url = f"http://127.0.0.1:8000/pdfToMd-text/"
    # api_url = f"http://127.0.0.1:8000/pdfToMd_docling/"

elif document_type_selectBox == 'PDF' and add_selectBox == 'Docling' and uploaded_file is not None:
    api_url = f"http://127.0.0.1:8000/pdfToMd_docling/"
else :
    api_url = None

if api_url is not None and uploaded_file is not None:
    try:
        response = requests.post(api_url,files={"file":uploaded_file})
        if response.status_code == 200 :
           
            # md_link = response.
            response_data = response.json()
            md_link = response_data.get("presigned_url")
            images_link = response_data.get("image_urls")
            tables_urls = response_data.get("table_url")

            # getting data from s3 link
            markdown_response = requests.get(md_link)

            if md_link:
                if markdown_response.status_code == 200:
                    md_data = markdown_response.text
                    st.markdown(md_data,unsafe_allow_html=True)
                else :
                    st.error("error: markdown")
            if images_link:
                for img in images_link:
                    st.image(img)
            if tables_urls:
                for table in tables_urls:
                  table_response = requests.get(table)
                  print(table_response)
                  df= pd.read_csv(table)
                  st.dataframe(df)
            
        else :
            st.error(f"Failed to process {requests.status_codes}")
    except requests.exceptions.RequestException as e :
        st.error("Error occured")
# else :
    # st.error("Select valid file")
        


