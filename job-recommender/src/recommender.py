import os
import pandas as pd
from dotenv import load_dotenv
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in your .env file.")

# Initialize embeddings model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

VECTORSTORE_PATH = "faiss_index"

# ---------------------------
# Store job data in FAISS
# ---------------------------
def upsert_jobs_in_vectorstore(jobs_df: pd.DataFrame):
    """
    Create or update a FAISS vector store with job postings.
    """
    if "description" not in jobs_df.columns:
        raise ValueError("jobs_df must have a 'description' column.")

    # Convert DataFrame to list of job descriptions
    job_texts = jobs_df["description"].tolist()
    metadatas = jobs_df.to_dict(orient="records")

    # Create FAISS store
    vectorstore = FAISS.from_texts(job_texts, embeddings, metadatas=metadatas)

    # Save locally
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✅ Stored {len(job_texts)} jobs in FAISS at {VECTORSTORE_PATH}")


# ---------------------------
# Recommend jobs
# ---------------------------
def recommend(query: str, top_k: int = 5) -> List[dict]:
    """
    Recommend top_k jobs based on the query from FAISS vector store.
    """
    if not os.path.exists(VECTORSTORE_PATH):
        raise FileNotFoundError("No FAISS index found. Please run upsert_jobs_in_vectorstore first.")

    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    results = vectorstore.similarity_search(query, k=top_k)

    recommendations = []
    for res in results:
        recommendations.append({
            "title": res.metadata.get("title", "Unknown"),
            "company": res.metadata.get("company", "Unknown"),
            "location": res.metadata.get("location", "Unknown"),
            "link": res.metadata.get("link", ""),
            "description": res.page_content
        })

    return recommendations
