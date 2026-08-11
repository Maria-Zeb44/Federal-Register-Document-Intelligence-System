import httpx
from typing import List, Dict, Any
from src.core.config import config

class FederalRegisterService:
    BASE_URL = config.FEDERAL_REGISTER_BASE_URL
    EXECUTIVE_ORDER_TYPE_ID = 2
    
    async def fetch_executive_orders(self, limit: int = 50) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/articles.json"
        params = {
            "conditions[type]": "PRESDOCU",
            "conditions[presidential_document_type_id]": self.EXECUTIVE_ORDER_TYPE_ID,
            "per_page": limit,
            "order": "newest"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])