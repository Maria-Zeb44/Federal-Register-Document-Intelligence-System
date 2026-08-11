from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str

class SourceResponse(BaseModel):
    document_id: int
    title: str
    executive_order_number: Optional[str]

class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceResponse]