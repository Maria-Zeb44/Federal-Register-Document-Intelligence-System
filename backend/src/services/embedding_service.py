from sentence_transformers import SentenceTransformer
from typing import List
from src.core.config import config

class EmbeddingService:
    def __init__(self):
        model_name = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"Model loaded! Dimension: {self.dimension}")
    
    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()
    
    def get_dimension(self) -> int:
        return self.dimension