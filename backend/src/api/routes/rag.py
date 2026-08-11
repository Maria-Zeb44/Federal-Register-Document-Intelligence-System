from fastapi import APIRouter, HTTPException, Query
from src.schemas.rag import QuestionRequest, AnswerResponse
from src.services.rag_service import RAGService
from typing import Optional

router = APIRouter(prefix="/api/rag", tags=["rag"])

@router.post("/query")
async def query_documents(
    request: QuestionRequest,
    document_id: Optional[int] = Query(None, description="Filter results to a specific document")
):
    if not request.question or len(request.question.strip()) < 3:
        raise HTTPException(status_code=400, detail="Question too short")
    
    try:
        service = RAGService()
        result = await service.generate_answer(
            question=request.question,
            document_id=document_id
        )
        return AnswerResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))