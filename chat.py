import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv




# ===================== CONFIG =====================

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

LLM_DEPLOYMENT = os.getenv("LLM_DEPLOYMENT")
EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT")
API_VERSION = os.getenv("API_VERSION")

SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
SEARCH_INDEX = os.getenv("SEARCH_INDEX")

# ===================== CLIENTS =====================

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

# ===================== RAG FUNCTIONS =====================

def embed_query(query: str):
    """Convert user question to embedding"""
    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=query
    )
    return response.data[0].embedding


def retrieve_context(question: str, top_k: int = 3):
    """
    Returns:
    - context_text (str or None)
    - top_score (float)
    - sources (list of str)
    """
    try:
        vector = embed_query(question)

        results = search_client.search(
            search_text=None,
            vector_queries=[{
                "kind": "vector",
                "vector": vector,
                "k": top_k,
                "fields": "embedding"
            }],
            select=["content", "source"]
        )

        contexts = []
        sources = set()
        top_score = 0.0

        for r in results:
            contexts.append(r["content"])

            if "source" in r:
                sources.add(r["source"])

            if "@search.score" in r:
                top_score = max(top_score, r["@search.score"])

        context_text = "\n".join(contexts).strip()

        return context_text, top_score, list(sources)

    except Exception as e:
        print("retrieve_context error:", e)
        # still return 3 values
        return None, 0.0, []








def build_rag_prompt(context: str, question: str):
    """Constructign  RAG prompt Here"""
    return f"""
You are an HR policy assistant.

Answer the question strictly using the context below.
If the answer is not present in the context, say "I do not have that information."

Context:
{context}

Question:
{question}

Answer:
"""

def build_general_prompt(question):
    return f"""
You are a helpful, professional AI assistant.

Answer the user's question clearly and concisely.

Question:
{question}

Answer:
"""



def generate_answer(prompt: str):
    """Generate final answer using LLM through api_call"""
    response = openai_client.chat.completions.create(
        model=LLM_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()



def ask_hr_bot(question: str):
    try:
        context, score, sources = retrieve_context(question)

        RELEVANCE_THRESHOLD = 0.55

        if context and score >= RELEVANCE_THRESHOLD:
            prompt = build_rag_prompt(context, question)
            mode = "RAG"
        else:
            prompt = build_general_prompt(question)
            mode = "GENERAL"
            sources = []
        #to ensure Rag is using which mode
        print(f"Mode: {mode}, Score: {score}")

        response = openai_client.chat.completions.create(
            model=LLM_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.4
        )

        return {
            "answer": response.choices[0].message.content.strip(),
            "mode": mode,
            "sources": sources
        }

    except Exception as e:
        print("ask_hr_bot error:", e)
        return {
            "answer": "Sorry, something went wrong.",
            "mode": "ERROR",
            "sources": []
        }






# Test loop for terminal or local testing

if __name__ == "__main__":
    print("\n🤖 HR Policy Chatbot (RAG Enabled)")
    print("Type 'exit' to quit\n")

    while True:
        question = input("You: ")
        if question.lower() == "exit":
            break

        answer = ask_hr_bot(question)
        print("\nBot:", answer)
        print("-" * 60)
