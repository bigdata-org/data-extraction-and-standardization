import streamlit as st
import requests
import pandas as pd

st.title('Pytract-PDF Analyzer')
st.markdown('---')

st.subheader("Existing PDFs")  
api_url = "http://52.4.147.70:8000"
list_object_endpoint = "/objects"
results_docint_endpoint = "/results/doc-int"
results_oss_endpoint = "/results/opensource"
results_docling_endpoint = "/results/docling"
df= pd.DataFrame()
try:
    obj_res = requests.get(api_url+list_object_endpoint)
    if obj_res.status_code==200:
        files = obj_res.json()
        df = pd.DataFrame(files)
        df.rename(columns={
            'file_name': 'File Name',
            'file_size': 'Size (KB)',
            'last_modified': 'Last Modified',
            'url': 'Public Endpoint'
        }, inplace=True)
    else:
        st.error('We’re unable to retrieve the list of PDFs at the moment. Please try again later or contact support if the issue persists')
except:
    st.error('Server is down..')

if df.empty:
    st.warning('No PDF files available to display. Please upload a file or check back later.')
else:          
    # Add a selection column
    df.insert(0, "Select", False)

    # Display table with row selection capability
    edited_df = st.data_editor(df, num_rows="dynamic", key="Public Endpoint", hide_index=True)

    selected_rows = edited_df[edited_df["Select"] == True]
    columns_to_display = [col for col in selected_rows.columns if col != 'Select']

    st.write("### Selected Files:")
    st.dataframe(selected_rows[columns_to_display], use_container_width=True, hide_index=True)

    tool_option = st.radio("Choose an option", ["Open Source (PyPDF, pdfplumber)", "Enterprise (Document Intelligence)"])

    if st.button('**Fetch**'):
        if selected_rows.shape[0]==1:
            file_name = selected_rows.iloc[0]["File Name"].strip('.pdf')
            endpoint = results_oss_endpoint if tool_option == "Open Source (PyPDF, pdfplumber)" else results_docint_endpoint        
            response = requests.get(api_url+endpoint+f'/{file_name}')
            if response.status_code==200:
                result = response.json()
                img_df = pd.DataFrame(result['images'])
                table_df = pd.DataFrame(result['tables'])
                with st.expander('Extracted Images'):
                    if img_df.shape[0]>0:
                        img_df.rename(columns={
                                            'file_name': 'File Name',
                                            'file_size': 'Size (KB)',
                                            'last_modified': 'Last Modified',
                                            'url': 'Public Endpoint'
                                        }, inplace=True)
                        st.dataframe(img_df, hide_index=True)
                    else:
                        st.warning('No Images Extracted')
                with st.expander('Extracted Tables'):
                    if table_df.shape[0]>0:
                        table_df.rename(columns={
                                            'file_name': 'File Name',
                                            'file_size': 'Size (KB)',
                                            'last_modified': 'Last Modified',
                                            'url': 'Public Endpoint'
                                        }, inplace=True)                
                        st.dataframe(table_df, hide_index=True)
                    else:
                        st.warning('No Tables Extracted') 
            else:
                st.error("Object Not Found")
            with st.expander('Markdown'):
                md_response = requests.get(api_url+results_docling_endpoint+f'/{file_name}')
                if md_response.status_code==200:
                    md_result = md_response.json()
                    st.subheader('Markdown')
                    st.markdown(md_result['md'])
                else:
                    st.error("Markdown Extraction Failed")

        elif selected_rows.shape[0]==0:
            st.warning("Select a PDF Record to fetch results")
        else :
            st.warning("Currently our system is synchronous!\nKindly queue one process at a time!")