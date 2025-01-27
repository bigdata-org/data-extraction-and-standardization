# Data Extraction and Standardization

An integrated solution for data processing and visualization using FastAPI and Streamlit.

## Project Overview

/data-extraction-and-standardization
│
├── backend
│ └── app.py # FastAPI backend application
│
└── frontend
└── streamlit-app.py # Streamlit frontend application

## Quick Start Guide

### Setup

1. **Clone the Repository**
git clone <repository-url>
cd data-extraction-and-standardization
text

2. **Configure Python Environment**
python -m venv .venv
For Unix/macOS
source .venv/bin/activate
For Windows
.venv\Scripts\activate
text

3. **Install Dependencies**
pip install -r requirements.txt
text

### Launch Applications

**Backend Service**
cd backend
uvicorn app:app --reload --port 8000
text

**Frontend Interface**
cd frontend
streamlit run streamlit-app.py --server.port=8501
text

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| FastAPI Docs | http://localhost:8000/docs | API documentation and testing interface |
| Streamlit App | http://localhost:8501 | User-friendly web interface |

---
