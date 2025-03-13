import streamlit as st
import requests
import json
from utils.helper import *
st.set_page_config(page_title="PDF Analyzer", layout="wide")
st.title("📄 PytractAI - The Q&A Engine")

model_mapper = {
    "openai/gpt-4o": "gpt-4o-2024-08-06",
    "openai/gpt-3.5-turbo": "gpt-3.5-turbo-0125",
    "openai/gpt-4": "gpt-4-0613",
    "openai/gpt-4o-mini": "gpt-4o-mini-2024-07-18",
    "gemini/gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini/gemini-2.0-flash-lite": "gemini/gemini-2.0-flash-lite"
}

available_models = list(model_mapper.keys())

if 'pdf_data' not in st.session_state:
    load_pdfs()
df = st.session_state.get('pdf_data').copy()
parsed_pdfs = df['File Name'].to_list()
# Streamlit UI Design


# Sidebar for Upload and Select
st.sidebar.header("Select PDF")

# # Select Parsed PDF Section
selected_pdf = st.sidebar.radio("Select a Parsed PDF", parsed_pdfs)
selected_model = st.sidebar.radio("LLM Model", available_models)
selected_row = df[df['File Name'] == selected_pdf].iloc[0]
pdf_endpoint = selected_row['Public Endpoint']
# # Main Panel for Functionality
st.subheader(f"Selected PDF: {pdf_endpoint}" if selected_pdf else "Select a PDF to Continue")

if selected_pdf and selected_model:
    tab1, tab2 = st.tabs(["📋 Summarize", "❓ Q&A"])

    with tab1:
        st.subheader("Summary")
        if st.button("Generate Summary"):
            data = {"url": pdf_endpoint, "model": selected_model}
            st.write(data)
            response = requests.post(base_url+summarize, json=data)
            st.write(response.json())
            if response.status_code == 200:
                st.success(response.json().get("markdown"))
            else:
                st.error("Error generating summary.")

    with tab2:
        st.subheader("Ask a Question")
        question = st.text_input("Enter your question:")
        if st.button("Ask"):
            if question:
                data = {"url": pdf_endpoint, "model": selected_model, "prompt": question}
                response = requests.post(base_url+ask_question, json=data)
                if response.status_code == 200:
                    st.success(response.json().get("markdown"))
                else:
                    st.error("Error generating answer.")
            else:
                st.warning('Invalid prompt')

# Style Enhancements
st.markdown("""
    <style>
        .stButton>button { width: 100%; border-r~adius: 10px; background-color: #4CAF50; color: white; }
        .stTextInput>div>div>input { border-radius: 10px; border: 2px solid #4CAF50; }
        .stRadio { border: 1px solid #4CAF50; border-radius: 10px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)