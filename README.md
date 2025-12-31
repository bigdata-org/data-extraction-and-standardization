# Pytract - Data Extraction & Standardization Platform

Pytract is an end-to-end **document and web data extraction platform** that ingests PDFs and URLs, extracts structured and unstructured content, standardizes it into Markdown, and enables **AI-powered summarization and Q&A** workflows.

It combines **open-source tooling** with **enterprise-grade services** (Azure Document Intelligence, Snowflake, Redis, LLMs) behind a FastAPI backend and a Streamlit UI.

## 🚀 Key Capabilities

- **PDF Ingestion & Storage** - Seamless AWS S3 integration for document management
- **Multi-Engine Extraction**
  - **Open-source**: PyPDF, pdfplumber, BeautifulSoup
  - **Enterprise**: Azure Document Intelligence
  - **Docling-based**: PDF → Markdown standardization
- **Web Scraping**
  - Firecrawl for Markdown-first scraping
  - BeautifulSoup-based HTML parsing
- **AI-Powered Workflows**
  - Document summarization with multiple LLM providers
  - Retrieval-Augmented Q&A (RAG) capabilities
- **Caching & Observability**
  - Redis for request-level caching
  - Snowflake for LLM inference logging
- **Unified Interface**
  - Complete workflow management through Streamlit UI

## 🧱 Architecture Overview

```
User
└── Streamlit Frontend
    └── FastAPI Backend
        ├── AWS S3 (PDFs, tables, images, markdown)
        ├── Extraction Engines
        │   ├── Docling
        │   ├── Azure Document Intelligence
        │   ├── PyPDF / pdfplumber
        │   ├── Firecrawl
        │   └── BeautifulSoup
        ├── Redis (caching)
        ├── Snowflake (LLM logs)
        └── LLM Providers (OpenAI, Gemini via LiteLLM)
```

## 📁 Project Structure

```
bigdata-org-data-extraction-and-standardization/
├── backend/                    # FastAPI backend
│   ├── app.py
│   ├── utils/
│   │   ├── aws/               # S3 utilities
│   │   ├── azure/             # Azure Document Intelligence
│   │   ├── docling/           # PDF → Markdown conversion
│   │   ├── firecrawl/         # Web scraping utilities
│   │   ├── haystack/          # RAG pipelines
│   │   ├── litellm/           # LLM abstraction layer
│   │   ├── opensource/        # Open-source PDF & web extractors
│   │   └── snowflake/         # LLM logging utilities
│   └── Dockerfile
├── frontend/                   # Streamlit UI
│   ├── streamlit-app.py
│   ├── pages/
│   │   ├── pytractPDF.py      # PDF extraction interface
│   │   ├── pytractView.py     # Results viewing
│   │   ├── pytractAI.py       # Summarization & Q&A
│   │   └── pytractWEB.py      # Web extraction interface
│   └── Dockerfile
├── redis/                      # Redis configuration
├── diag/                       # Architecture diagrams
└── prototyping/               # Experiments & notebooks
```

## ⚙️ Prerequisites

- **Python 3.10+**
- **Docker** (recommended for deployment)
- **AWS Account** with S3 access
- **Azure Document Intelligence** (optional, for enterprise extraction)
- **Snowflake Account** (optional, for logging)
- **Redis** instance

## 🔐 Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BUCKET_NAME=your-s3-bucket-name

# Azure Document Intelligence (Optional)
AZURE_DOC_INT_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOC_INT_KEY=your_azure_key

# Snowflake Configuration (Optional)
SF_USER=your_snowflake_user
SF_PASSWORD=your_snowflake_password
SF_ACCOUNT=your_account_identifier
SF_WAREHOUSE=your_warehouse
SF_DB=your_database
SF_ROLE=your_role

# LLM Provider APIs
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🚦 Quick Start

### Option 1: Local Development

**1. Backend Setup**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

**2. Frontend Setup** (in a new terminal)
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit-app.py --server.port=8501
```

**3. Access the Application**
- **Streamlit UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### Option 2: Docker Deployment

**1. Backend Container**
```bash
cd backend
docker build -t pytract-backend .
docker run -p 8000:8000 --env-file .env pytract-backend
```

**2. Frontend Container**
```bash
cd frontend
docker build -t pytract-frontend .
docker run -p 8501:8501 pytract-frontend
```

**3. Redis Setup** (if needed)
```bash
cd redis
docker-compose up -d
```

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload PDF documents to S3 |
| POST | `/extract/docling` | Convert PDF to standardized Markdown |
| POST | `/extract/doc-int` | Extract using Azure Document Intelligence |
| POST | `/extract/opensource` | Extract using open-source tools |
| POST | `/scrape/firecrawl` | Web scraping with Markdown output |
| POST | `/text-summarize` | AI-powered document summarization |
| POST | `/qa` | RAG-based question answering |
| GET | `/results/*/{id}` | Retrieve extraction results |

### Example Usage

**Upload and Extract PDF**
```bash
# Upload PDF
curl -X POST "http://localhost:8000/upload" \
     -F "file=@document.pdf"

# Extract with Docling
curl -X POST "http://localhost:8000/extract/docling" \
     -H "Content-Type: application/json" \
     -d '{"file_url": "s3://bucket/document.pdf"}'
```

**Web Scraping**
```bash
curl -X POST "http://localhost:8000/scrape/firecrawl" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

**AI Summarization**
```bash
curl -X POST "http://localhost:8000/text-summarize" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your document content here", "provider": "openai"}'
```

## 🧠 AI & RAG Architecture

### Document Processing Pipeline
1. **Ingestion**: PDFs uploaded to S3 storage
2. **Extraction**: Multiple engines convert documents to structured format
3. **Standardization**: Content normalized to Markdown format
4. **Indexing**: Documents chunked and embedded for retrieval

### RAG Implementation
- **Indexing**: Markdown content → semantic chunks → vector embeddings
- **Retrieval**: In-memory vector store for fast similarity search
- **Generation**: Prompt-engineered responses using multiple LLM providers
- **Caching**: Redis prevents duplicate processing and improves response times

### LLM Integration
- **Multi-Provider Support**: OpenAI, Google Gemini via LiteLLM abstraction
- **Intelligent Routing**: Automatic fallback between providers
- **Observability**: All LLM interactions logged to Snowflake

## 🏭 Production Features

### Performance & Scalability
- **Stateless API Design**: Horizontally scalable backend
- **Intelligent Caching**: Redis-based request deduplication
- **Async Processing**: Non-blocking extraction workflows
- **Resource Management**: Configurable limits and timeouts

### Monitoring & Observability
- **Comprehensive Logging**: All operations tracked and stored
- **Error Handling**: Graceful degradation with retry logic
- **Performance Metrics**: Response times and success rates monitored
- **Cost Tracking**: LLM usage and costs logged to Snowflake

### Security
- **Environment-based Configuration**: Secure credential management
- **Input Validation**: Comprehensive request sanitization
- **Rate Limiting**: API endpoint protection
- **Access Control**: Role-based permissions support

## 🎯 Use Cases

### Enterprise Applications
- **Document Digitization**: Convert legacy PDFs to searchable, structured formats
- **Knowledge Base Creation**: Build searchable repositories from unstructured content
- **Compliance & Legal**: Extract and standardize regulatory documents
- **Financial Analysis**: Process reports, statements, and market research

### Research & Development
- **Academic Papers**: Summarize and extract insights from research publications
- **Patent Analysis**: Structure and analyze patent documents
- **Market Intelligence**: Extract insights from industry reports and web content
- **Competitive Analysis**: Monitor and analyze competitor information

## 🛠️ Configuration Options

### Extraction Engines
```python
# Configure extraction preferences
EXTRACTION_ENGINES = {
    "docling": {"priority": 1, "markdown_quality": "high"},
    "azure_doc_int": {"priority": 2, "structured_data": True},
    "opensource": {"priority": 3, "fallback": True}
}
```

### LLM Providers
```python
# LLM provider configuration
LLM_CONFIG = {
    "openai": {"model": "gpt-4", "temperature": 0.1},
    "gemini": {"model": "gemini-pro", "temperature": 0.1},
    "fallback_order": ["openai", "gemini"]
}
```

### Caching Strategy
```python
# Redis caching configuration
CACHE_CONFIG = {
    "ttl": 3600,  # 1 hour
    "max_size": "1GB",
    "compression": True
}
```

## 🔧 Troubleshooting

### Common Issues

**Environment Variables Not Loading**
```bash
# Verify .env file location and format
python -c "import os; print(os.getenv('AWS_ACCESS_KEY_ID'))"
```

**S3 Upload Failures**
```bash
# Check AWS credentials and bucket permissions
aws s3 ls s3://your-bucket-name --profile your-profile
```

**Azure Document Intelligence Issues**
```bash
# Verify endpoint and key configuration
curl -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
     "YOUR_ENDPOINT/formrecognizer/info"
```

**Redis Connection Problems**
```bash
# Test Redis connectivity
redis-cli ping
```

**LLM API Failures**
- Check API keys and quota limits
- Verify provider-specific configuration
- Review error logs in Snowflake (if configured)

## 📊 Monitoring & Logs

### Application Logs
- **Backend**: FastAPI request/response logs
- **Extraction**: Processing status and error details
- **AI Operations**: LLM request/response tracking

### Performance Metrics
- **Response Times**: API endpoint performance
- **Success Rates**: Extraction and processing accuracy
- **Resource Usage**: Memory, CPU, and storage utilization
- **Cost Analytics**: LLM usage and associated costs

---

**Built for Enterprise-Grade Document Intelligence** 🚀
