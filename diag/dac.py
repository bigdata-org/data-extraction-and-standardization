from diagrams import Diagram, Cluster
from diagrams.onprem.client import Users
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.aws.network import Endpoint

from diagrams.custom import Custom
from diagrams.azure.ml import CognitiveServices

with Diagram("Extraction Pipeline", filename='diag/arch_diag') as diag:
    
    user = Users("User")

    with Cluster("Frontend"):
        frontend = Custom("Streamlit Cloud", 'images/streamlit.png')

    with Cluster("Backend"):
        backend = FastAPI("FastAPI Server")

    with Cluster("PDF Extractor Cluster"):
        docling = Python("Docling")  # Custom image
        azure_ai = CognitiveServices("Azure Document Intelligence")
        python_libs = Python("PyPDF, pdfplumber")

    with Cluster("Web Extractor Cluster"):
        firecrawl = Endpoint("Firecrawl")  # Custom image
        beautifulsoup = Python("BeautifulSoup")

    # Connections
    user >> frontend >> backend  
    backend >> docling  
    backend >> azure_ai  
    backend >> python_libs  
    backend >> firecrawl  
    backend >> beautifulsoup  
diag