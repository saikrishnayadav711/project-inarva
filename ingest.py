import os
from dotenv import load_dotenv

load_dotenv()
import uuid
from PyPDF2 import PdfReader
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Configuration from environment variables


AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT")
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT")
API_VERSION = os.getenv("API_VERSION")

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX")

#clients for OpenAI and Azure Search

openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=API_VERSION
)

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)

#Functions for PDF ingestion

def extract_text(pdf_path):
    """Extract text from a text-based PDF"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += max(chunk_size - overlap, 1)

    return chunks


def embed_text(text):
    """Generate embedding and verify dimension"""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text
    )
    vector = response.data[0].embedding
    print("   🔹 Embedding length:", len(vector))
    return vector


def upload_chunks(chunks, source):
    """Upload chunks to Azure AI Search with logging"""
    if not chunks:
        print(f"No chunks to upload for {source}")
        return

    documents = []
    for chunk in chunks:
        documents.append({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "embedding": embed_text(chunk),
            "source": source
        })

    print(f"⬆Uploading {len(documents)} chunks from {source}")
    results = search_client.upload_documents(documents)

    for r in results:
        if r.succeeded:
            print("   ✅ Chunk uploaded")
        else:
            print("   ❌ Upload failed:", r.error_message)


# ===================== MAIN PIPELINE =====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDER = os.path.join(BASE_DIR, "data")

print("\nPDF folder:", PDF_FOLDER)

if not os.path.exists(PDF_FOLDER):
    raise FileNotFoundError("data/hr_policies folder not found")

pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    raise RuntimeError("No PDF files found in hr_policies folder")

for file in pdf_files:
    print(f"\nProcessing file: {file}")
    path = os.path.join(PDF_FOLDER, file)

    text = extract_text(path)
    print("Extracted text length:", len(text))

    if len(text) == 0:
        print("❌ No text extracted (PDF may be scanned). Skipping.")
        continue

    chunks = chunk_text(text)
    print("Number of chunks:", len(chunks))

    upload_chunks(chunks, file)

print("\nHR document ingestion completed successfully.")
