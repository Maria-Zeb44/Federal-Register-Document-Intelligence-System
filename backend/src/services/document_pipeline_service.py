from typing import List, Dict, Any
from src.services.federal_register_service import FederalRegisterService
from src.services.pdf_service import PDFService
from src.services.embedding_service import EmbeddingService
from src.core.database import Database
from src.core.config import config

class DocumentPipelineService:
    def __init__(self):
        self.db = Database()
        self.api = FederalRegisterService()
        self.pdf = PDFService()
        self.embedding = EmbeddingService()
    
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
    
    def save_document(self, order: Dict[str, Any], full_text: str):
        try:
            # Check if document already exists
            existing = self.db.execute_query(
                "SELECT id FROM documents WHERE document_number = %s",
                (order.get("document_number"),),
                fetch=True
            )
            if existing:
                print(f"   ⏭️ Document already exists (ID: {existing[0]['id']})")
                return existing[0]['id']
            
            # Insert new document
            query = """
                INSERT INTO documents (
                    document_number, title, abstract, executive_order_number,
                    publication_date, pdf_url, html_url, full_text
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            result = self.db.execute_query(query, (
                order.get("document_number"),
                order.get("title", "Untitled"),
                order.get("abstract", ""),
                order.get("executive_order_number"),
                order.get("publication_date"),
                order.get("pdf_url"),
                order.get("html_url"),
                full_text
            ), fetch=True)
            
            if result:
                doc_id = result[0]['id']
                print(f"   ✅ Saved document (ID: {doc_id})")
                return doc_id
            else:
                print("   ❌ Failed to save document - no ID returned")
                return None
                
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return None
    
    def store_chunks(self, document_id: int, chunks: List[str]):
        if not chunks or not document_id:
            return 0
        
        try:
            embeddings = self.embedding.generate_embeddings(chunks)
            
            stored_count = 0
            for j, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                self.db.execute_query(
                    "INSERT INTO document_chunks (document_id, chunk_text, embedding, chunk_index) VALUES (%s, %s, %s::vector, %s)",
                    (document_id, chunk, embedding, j)
                )
                stored_count += 1
            
            return stored_count
        except Exception as e:
            print(f"   ❌ Error storing chunks: {e}")
            return 0
    
    async def run_full_pipeline(self, limit: int = 50): 
        results = {
            "fetched": 0,
            "processed": 0,
            "chunks_created": 0,
            "errors": []
        }
        
        print(f"\n🚀 Starting pipeline for {limit} Executive Orders...")
        print("=" * 60)
        
        orders = await self.api.fetch_executive_orders(limit)
        results["fetched"] = len(orders)
        print(f"✅ Fetched {len(orders)} Executive Orders")
        print("=" * 60)
        
        for i, order in enumerate(orders, 1):
            try:
                title = order.get('title', 'Unknown')[:50]
                print(f"\n📄 [{i}/{len(orders)}] Processing: {title}...")
                
                pdf_url = order.get("pdf_url")
                if not pdf_url:
                    print("   ⚠️ No PDF URL, skipping")
                    results["errors"].append(f"No PDF URL: {order.get('document_number')}")
                    continue
                
                pdf_text = await self.pdf.extract_text_from_url(pdf_url)
                if not pdf_text:
                    print("   ⚠️ No text extracted, skipping")
                    results["errors"].append(f"PDF extraction failed: {order.get('document_number')}")
                    continue
                print(f"   📄 Extracted {len(pdf_text)} characters")
                
                doc_id = self.save_document(order, pdf_text)
                if not doc_id:
                    print("   ❌ Failed to save document, skipping chunks")
                    results["errors"].append(f"Document save failed: {order.get('document_number')}")
                    continue
                
                chunks = self.chunk_text(pdf_text)
                if not chunks:
                    print("   ⚠️ No chunks created")
                    continue
                print(f"   📦 Created {len(chunks)} chunks")
                
                stored = self.store_chunks(doc_id, chunks)
                results["chunks_created"] += stored
                results["processed"] += 1
                print(f"   ✅ Stored {stored} chunks with embeddings")
                
            except Exception as e:
                error_msg = f"Error on {order.get('document_number', 'unknown')}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"   ❌ {error_msg}")
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print(f"   📄 Documents fetched: {results['fetched']}")
        print(f"   💾 Documents processed: {results['processed']}")
        print(f"   📦 Chunks created: {results['chunks_created']}")
        if results["errors"]:
            print(f"   ⚠️ Errors: {len(results['errors'])}")
        print("=" * 60)
        
        return results