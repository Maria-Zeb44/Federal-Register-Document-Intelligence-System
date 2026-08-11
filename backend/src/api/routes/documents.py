from fastapi import APIRouter, Query, HTTPException
from src.services.document_pipeline_service import DocumentPipelineService

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/collect")
async def collect_documents(limit: int = Query(50, ge=1, le=100)):
    try:
        service = DocumentPipelineService()
        results = await service.run_full_pipeline(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_documents(limit: int = Query(50, ge=1, le=100)):
    service = DocumentPipelineService()
    db = service.db
    results = db.execute_query(
        "SELECT id, document_number, title, abstract, executive_order_number, publication_date, pdf_url, html_url FROM documents ORDER BY created_at DESC LIMIT %s",
        (limit,),
        fetch=True
    )
    return {"documents": results}

@router.get("/{document_id}")
async def get_document(document_id: int):
    service = DocumentPipelineService()
    db = service.db
    result = db.execute_one(
        "SELECT * FROM documents WHERE id = %s",
        (document_id,)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return result