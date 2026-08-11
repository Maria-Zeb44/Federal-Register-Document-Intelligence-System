from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# ============================================
# DOCUMENT SCHEMAS
# ============================================

class DocumentBase(BaseModel):
    """Base document model with common fields"""
    document_number: str
    title: str
    abstract: Optional[str] = None
    executive_order_number: Optional[str] = None
    publication_date: Optional[date] = None
    pdf_url: Optional[str] = None
    html_url: Optional[str] = None

class DocumentCreate(DocumentBase):
    """Schema for creating a new document (includes full_text)"""
    full_text: Optional[str] = None

class DocumentResponse(DocumentBase):
    """Schema for document list response (excludes full_text)"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document view (includes full_text)"""
    full_text: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Schema for paginated document list"""
    documents: list[DocumentResponse]
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    total_pages: Optional[int] = None

# ============================================
# SEARCH SCHEMAS
# ============================================

class DocumentSearchParams(BaseModel):
    """Schema for document search parameters"""
    q: Optional[str] = None
    executive_order_number: Optional[str] = None
    publication_date_start: Optional[date] = None
    publication_date_end: Optional[date] = None
    limit: int = 50
    page: int = 1

# ============================================
# DOCUMENT CHUNK SCHEMAS
# ============================================

class DocumentChunkBase(BaseModel):
    """Base chunk model"""
    document_id: int
    chunk_text: str
    chunk_index: int

class DocumentChunkResponse(DocumentChunkBase):
    """Schema for chunk response"""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentChunkWithEmbedding(DocumentChunkResponse):
    """Schema for chunk with embedding (for internal use)"""
    embedding: Optional[list[float]] = None

# ============================================
# DOCUMENT WITH CHUNKS SCHEMA
# ============================================

class DocumentWithChunks(DocumentDetailResponse):
    """Schema for document with its chunks"""
    chunks: list[DocumentChunkResponse] = []