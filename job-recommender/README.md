# AI-Powered Job Recommendation System (Live)

Streamlit app that:
- Fetches **live job postings** from SerpAPI (Google Jobs) and/or JSearch (RapidAPI)
- Indexes results in a local **vector store** (Chroma)
- Uses **LangChain + Gemini** to generate short **personalized explanations**
- No resume upload required

## ⚙️ Tech
- Python, Streamlit
- LangChain + Google Gemini (gemini-1.5-flash, text-embedding-004)
- Chroma vector DB
- SerpAPI (Google Jobs) and/or JSearch (RapidAPI)

## 🚀 Run Locally

```bash
python -m venv venv

# PowerShell (allow scripts for this session)

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

# put your keys in .env (GEMINI_API_KEY, optional SERPAPI_KEY, RAPIDAPI_KEY)

streamlit run app.py



---

## Quick Start (your exact run flow on Windows PowerShell)

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then open .env and paste your keys
streamlit run app.py


# 1. Create virtual environment
python -m venv venv

# 2. (Optional, only if PowerShell blocks venv activation)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Activate venv
venv\Scripts\activate

# 4. Install main dependencies
pip install -r requirements.txt

# 5. Install missing packages
pip install faiss-cpu
pip install langchain-community

# 6. Copy environment file and add keys
copy .env.example .env
notepad .env   # edit with your API keys


