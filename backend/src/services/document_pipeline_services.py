from typing import List
from src.core.database import Database
from src.services.embedding_service import get_embedding_service
from src.services.federal_register_service import FederalRegisterService
from src.services.pdf_service import PDFService
from src.core.config import config

class DocumentPipelineService:
    def __init__(self):  # ← FIXED: added spaces and parentheses
        self.db = Database()
        self.api = FederalRegisterService()
        self.pdf = PDFService()
        self.embedding_service = get_embedding_service()
        self.base_url = config.FEDERAL_REGISTER_BASE_URL
        self.executive_order_type_id = 2
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_service.generate_embeddings(texts)
    
    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        chunk_size = config.CHUNK_SIZE
        overlap = config.CHUNK_OVERLAP
        
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            if end < text_length:
                for i in range(end, max(start, end - 200), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    async def run_full_pipeline(self, limit: int = 5):
        # Your pipeline logic here
        pass