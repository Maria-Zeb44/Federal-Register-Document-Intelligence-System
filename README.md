# Federal Register Document Intelligence System

A small toolkit for collecting, processing, embedding, and querying Executive Orders from the Federal Register using a RAG (Retrieval-Augmented Generation) pipeline.

Features
- Collect Executive Orders from the Federal Register API
- Chunk and embed documents using `sentence-transformers`
- Store and query document chunks via a simple RAG API
- Streamlit UI for browsing documents and asking questions

Repository layout
- `backend/` — FastAPI backend and services (document ingestion, embeddings, RAG endpoints)
- `streamlit-frontend/` — Streamlit application that consumes the backend API
- `database_schema.sql` — Example DB schema used by the project

Quickstart

Prerequisites
- Python 3.10+ installed
- Git

Backend
1. Create and activate a virtual environment, install dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
pip install -r requirements.txt
```

2. Create a `.env` file in `backend/` with at minimum a `DATABASE_URL`. Example:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/fr_docs
# Optional: GROQ_API_KEY, EMBEDDING_MODEL, EMBEDDING_DIMENSION
```

3. Run the API (from `backend/`):

```powershell
# from backend directory
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (Streamlit)
1. Install Streamlit (globally or in a venv) and run the app:

```powershell
cd ../streamlit-frontend
pip install streamlit requests
streamlit run app.py
```

Notes
- The backend uses `sentence-transformers` for embeddings by default. Set `EMBEDDING_MODEL` and `EMBEDDING_DIMENSION` in `backend/.env` to customize (see `backend/src/core/config.py`).
- The Streamlit app expects the backend at `http://localhost:8000` by default.

Development
- Tests/snippets: see `backend/test_db_connection.py` and `backend/test_embedding.py` for examples.

Contributing
- Open an issue or PR on GitHub. Keep changes small and focused.

License
- MIT (add your preferred license)

Contact
- Maintainer: repository owner
