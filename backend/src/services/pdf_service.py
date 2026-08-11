import httpx
import io
from pypdf import PdfReader

class PDFService:
    async def extract_text_from_url(self, pdf_url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(pdf_url)
                response.raise_for_status()
                
                pdf_file = io.BytesIO(response.content)
                reader = PdfReader(pdf_file)
                
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""