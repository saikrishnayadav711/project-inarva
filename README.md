# HR Policy Hybrid RAG Chatbot

An enterprise-style AI chatbot built using **Azure OpenAI** and **Azure AI Search** that answers HR policy questions using **Retrieval-Augmented Generation (RAG)** while also supporting normal conversational (general-purpose) chatbot interactions.


---

## 🚀 Key Features

- Hybrid chatbot (HR policy RAG + general chatbot fallback)
- Azure OpenAI for LLM responses and embeddings
- Azure AI Search as a vector database
- Score-based relevance gating (threshold-based decision logic)
- FastAPI backend
- HTML + CSS frontend using Jinja2 templates
- Visual badges indicating response source
- PDF citations for policy-based answers
- Secure configuration using environment variables

---

## 🧠 How the System Works

1. User submits a question via the web interface
2. The question is converted into an embedding using Azure OpenAI
3. Vector similarity search is performed on HR policy documents
4. If the relevance score ≥ threshold (0.55):
   - The answer is generated using RAG (policy documents)
5. Otherwise:
   - The system falls back to a general chatbot response
6. The UI displays:
   - A badge indicating response type
   - PDF citations (only for RAG responses)

---

## 📁 Project Structure
project-inarva/
│
├── api.py # FastAPI application (routes + HTML rendering)
├── chat.py # Hybrid RAG + fallback chatbot logic
├── ingest.py # PDF ingestion and embedding pipeline
├── requirements.txt # Python dependencies
│
├── .env # Local environment variables (NOT committed)
├── .env.example # Template for environment variables
│
├── data/
│ └── hr_policies/ # HR policy PDFs (text-based)
│
├── templates/
│ └── index.html # HTML UI (Jinja2 template)
│
├── static/
│ └── style.css # CSS styling
│
├── docs/ # Optional documentation
│
├── .gitignore
├── README.md

## ⚙️ Setup Instructions

1️⃣ Clone the Repository
git clone https://github.com/your-username/project-inarva.git
cd project-inarva

2️⃣ Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate   # In Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file in the project root and add your credentials:

AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_openai_key_here

AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your_search_admin_key_here

LLM_DEPLOYMENT=Your_deployment_name
EMBEDDING_DEPLOYMENT=Your_embedding deployment_name
API_VERSION=2024-02-01

Run the ingestion script:
python ingest.py

▶️ Run the Application

Start the FastAPI server:
uvicorn api:app --reload


Open your browser:
http://127.0.0.1:8000 (Your can use azure ngrok or similar to expose publicly)

🛠️ Technologies Used

Python

FastAPI

Azure OpenAI

Azure AI Search

Jinja2

HTML & CSS

Vector Search (RAG)

🔐 Security Practices

API keys stored in .env

Secrets excluded via .gitignore

Environment-based configuration

🔮 Future Enhancements

Authentication and role-based access

Chat history persistence

OCR support for scanned PDFs

Cloud deployment (Azure App Service)

Semantic hybrid search