from utils.aws.s3 import read_markdown_from_s3
from utils.litellm.core import llm
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.converters import TextFileToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.writers import DocumentWriter
from haystack.components.builders import PromptBuilder, ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.components.converters import MarkdownToDocument
from haystack.dataclasses.byte_stream import ByteStream

def index(s3_client, url):
    try:
        file_name = url.split('uploads/')[1].strip('.pdf')
        markdown_bytes = read_markdown_from_s3(s3_client, file_name)[0]
        markdown_stream = ByteStream(data=markdown_bytes, mime_type="text/markdown")
        
        document_store = InMemoryDocumentStore()
        converter = MarkdownToDocument()
        cleaner = DocumentCleaner()
        splitter = DocumentSplitter()
        embedder = OpenAIDocumentEmbedder()
        writer = DocumentWriter(document_store)
        
        indexing_pipeline = Pipeline()
        indexing_pipeline.add_component("converter", converter)
        indexing_pipeline.add_component("cleaner", cleaner)
        indexing_pipeline.add_component("splitter", splitter)
        indexing_pipeline.add_component("embedder", embedder)
        indexing_pipeline.add_component("writer", writer)
        
        indexing_pipeline.connect("converter.documents", "cleaner.documents")
        indexing_pipeline.connect("cleaner.documents", "splitter.documents")
        indexing_pipeline.connect("splitter.documents", "embedder.documents")
        indexing_pipeline.connect("embedder.documents", "writer.documents")
        indexing_pipeline.run(data={"sources": [markdown_stream]})
        
        return document_store
    except:
        return -1

def rag(document_store, model, query):
    text_embedder = OpenAITextEmbedder()
    retriever = InMemoryEmbeddingRetriever(document_store)
    prompt_template = [
    ChatMessage.from_user(
        """
        Given the following documents, answer the question in **Markdown format**.
        
        ## Documents:
        {% for doc in documents %}
        - **Document {{ loop.index }}:**  
          {{ doc.content }}
        
        {% endfor %}
        
        ## Question:
        **{{query}}**
        
        ---
        
        ## Answer:
        Format the response in the markdown format using:
        - Headings (`##`, `###`)
        - Bullet points (`-`, `*`)
        - Tables (if necessary)
        - Properly formatted code blocks for technical content (` ``` `)
        
        If the provided documents do not contain enough information to answer the question, please strictly state:
        "I do not know the answer based on the provided context."
        """
    )
]
    prompt_builder = ChatPromptBuilder(template=prompt_template)
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("text_embedder", text_embedder)
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)

    rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
    rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
    result = rag_pipeline.run(data={"prompt_builder": {"query":query}, "text_embedder": {"text": query}})
    prompt = result['prompt_builder']['prompt'][0]._content[0].text
    response = llm(model,prompt)
    return response['markdown'] if 'markdown' in response else 'Something went wrong, no markdown key in response'

def generate_summary(s3_client, model, url):
    file_name = url.split('uploads/')[1].strip('.pdf')
    try:
        markdown_data = read_markdown_from_s3(s3_client, file_name)
        markdown_content = markdown_data[0].decode('utf-8')
    except (UnicodeDecodeError, IndexError, AttributeError, Exception) as e:
        raise Exception("File Not Found") from e

    prompt_template = [
        ChatMessage.from_user(
            """
            Given the following text, generate a concise and coherent summary in **Markdown format**.

            ## Text:
            {{ text }}

            ---

            ## Summary:
            - Summarize the content while preserving key information.
            - Keep the summary clear and structured.
            - Use bullet points (`-`, `*`) for key points if necessary.
            - Maintain the original meaning without adding new information.
            - Ensure the summary is well-formatted and easy to read.
            """
        )
    ]

    prompt_builder = ChatPromptBuilder(template=prompt_template)
    result = prompt_builder.run(text=markdown_content)
    prompt = result['prompt'][0]._content[0].text
    response = llm(model, prompt)
    return response.get('markdown','Something went wrong, no markdown key in response')

def qa(s3_client, url, prompt, model="gemini/gemini-1.5-pro",):
    document_store = index(s3_client, url)
    if isinstance(document_store, int):
        return 'Failure occured while indexing the pdf'
    answer = rag(document_store=document_store, model=model, query=prompt)
    return answer

def summarize(s3_client, url, model="gemini/gemini-1.5-pro",):
    summary = generate_summary(s3_client, model, url )
    return summary
     
