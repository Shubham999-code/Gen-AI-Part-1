import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing. Put it in your .env")

# text-embedding-004 is Gemini’s high-quality embedding model.
def get_embedder() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(model="text-embedding-004", google_api_key=GEMINI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    emb = get_embedder()
    return emb.embed_documents(texts)

def embed_query(q: str) -> List[float]:
    emb = get_embedder()
    return emb.embed_query(q)
