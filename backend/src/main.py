from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, documents, rag

app = FastAPI(
    title="Federal Register Document Intelligence System",
    description="Collect, process, and query Executive Orders using RAG",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(rag.router)

@app.get("/")
async def root():
    return {"message": "Federal Register Document Intelligence System API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}