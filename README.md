# data-extraction-and-standardization
This is a Pdf Scrapper for scrapping Text, images and tables.

## 📌 Setup Instructions
## 1️⃣ Clone the Repository  
cd data-extraction-and-standardization

## 2️⃣ Configure Python Environment
python -m venv .venv
For Unix/macOS: source .venv/bin/activate

For Windows: .venv\Scripts\activate

## 3️⃣ Install Dependencies
pip install -r requirements.txt

## 4️⃣ Launch Applications
uvicorn app:app --reload --port 8000

cd frontend
streamlit run streamlit-app.py 

## 🌐 Access Points

FastAPI Docs	http://localhost:8000/docs	API documentation and testing interface
Streamlit App	http://localhost:8501	User-friendly web interface



