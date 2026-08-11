from groq import Groq
from src.services.embedding_service import EmbeddingService
from src.core.database import Database
from src.core.config import config
from typing import Optional, List, Dict, Any

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service for Executive Orders.
    Handles document retrieval, embedding search, and answer generation.
    """
    
    def __init__(self):
        """Initialize RAG service with database, embedding model, and Groq client."""
        try:
            self.db = Database()
            self.embedding = EmbeddingService()
            self.groq = Groq(api_key=config.GROQ_API_KEY)
            self.model = config.GROQ_TEXT_MODEL
            self.top_k = 5  # Number of chunks to retrieve
            print("✅ RAGService initialized")
        except Exception as e:
            print(f"❌ RAGService init error: {e}")
            raise
    
    async def generate_answer(
        self, 
        question: str, 
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question using RAG.
        
        Args:
            question: The user's question
            document_id: Optional document ID to restrict search to a specific document
            
        Returns:
            Dictionary with 'answer' and 'sources'
        """
        try:
            print(f"\n" + "=" * 60)
            print(f"📝 Question: {question}")
            print(f"📄 Document ID: {document_id}")
            print("=" * 60)
            
            # Step 1: Generate query embedding
            try:
                query_embedding = self.embedding.generate_embedding(question)
                print("✅ Query embedding generated (dimension: 384)")
            except Exception as e:
                print(f"❌ Embedding generation failed: {e}")
                return {
                    "answer": f"Error generating embedding: {str(e)}",
                    "sources": []
                }
            
            # Step 2: Retrieve relevant chunks
            chunks = await self._retrieve_chunks(question, query_embedding, document_id)
            
            if not chunks:
                doc_msg = "this document" if document_id else "the documents"
                return {
                    "answer": f"I couldn't find relevant information in {doc_msg} to answer your question. Please try rephrasing or asking about specific content in the document.",
                    "sources": []
                }
            
            # Step 3: Build context from chunks
            context = self._build_context(chunks, document_id)
            
            # Step 4: Generate answer using Groq
            answer = await self._generate_groq_response(question, context, document_id)
            
            # Step 5: Prepare sources
            sources = [
                {
                    "document_id": c['document_id'],
                    "title": c['title'],
                    "executive_order_number": c.get('executive_order_number', 'N/A')
                }
                for c in chunks
            ]
            
            print(f"✅ Generated answer ({len(answer)} characters)")
            print(f"📚 Sources: {len(sources)} documents referenced")
            print("=" * 60)
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }
    
    async def _retrieve_chunks(
        self,
        question: str,
        query_embedding: List[float],
        document_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from the database using vector similarity search.
        
        Args:
            question: The user's question (for logging)
            query_embedding: The embedding vector of the question
            document_id: Optional document ID to filter by
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            if document_id:
                # Search only within the specified document
                print(f"🔍 Searching ONLY in document ID: {document_id}")
                search_query = """
                    SELECT 
                        dc.chunk_text, 
                        d.id as document_id, 
                        d.title, 
                        d.executive_order_number
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE dc.document_id = %s
                    ORDER BY dc.embedding <=> %s::vector
                    LIMIT %s
                """
                params = (document_id, query_embedding, self.top_k)
                chunks = self.db.execute_query(search_query, params, fetch=True)
                print(f"🔍 Found {len(chunks)} chunks in document {document_id}")
            else:
                # Search across all documents
                print("🔍 Searching across ALL documents")
                search_query = """
                    SELECT 
                        dc.chunk_text, 
                        d.id as document_id, 
                        d.title, 
                        d.executive_order_number
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    ORDER BY dc.embedding <=> %s::vector
                    LIMIT %s
                """
                params = (query_embedding, self.top_k)
                chunks = self.db.execute_query(search_query, params, fetch=True)
                print(f"🔍 Found {len(chunks)} chunks across all documents")
            
            return chunks
            
        except Exception as e:
            print(f"❌ Chunk retrieval error: {e}")
            return []
    
    def _build_context(
        self, 
        chunks: List[Dict[str, Any]], 
        document_id: Optional[int] = None
    ) -> str:
        """
        Build a context string from the retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries
            document_id: Optional document ID to customize references
            
        Returns:
            Formatted context string for the prompt
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            # Get document reference
            eo_num = chunk.get('executive_order_number') or 'N/A'
            
            if document_id:
                # Single document context
                doc_ref = f"This Document (EO #{eo_num})"
            else:
                # Multiple documents context
                doc_title = chunk.get('title', 'Unknown Document')[:60]
                doc_ref = f"Document {i}: {doc_title} (EO #{eo_num})"
            
            # Add chunk text with reference
            context_parts.append(f"{doc_ref}:\n{chunk['chunk_text']}")
        
        return "\n\n---\n\n".join(context_parts)
    
    async def _generate_groq_response(
        self,
        question: str,
        context: str,
        document_id: Optional[int] = None
    ) -> str:
        """
        Generate an answer using Groq's LLM.
        
        Args:
            question: The user's question
            context: The retrieved context
            document_id: Optional document ID to customize the prompt
            
        Returns:
            Generated answer string
        """
        try:
            # Build system prompt
            system_prompt = (
                "You are a helpful assistant that answers questions based ONLY on the provided documents. "
                "Be accurate, concise, and cite information from the specified documents. "
                "If the documents don't contain the information, say so clearly."
            )
            
            # Build user prompt based on document context
            if document_id:
                user_prompt = f"""Based on the document provided below, answer the user's question.

IMPORTANT: Use ONLY information from this document. Do NOT use external knowledge or information from other documents.

DOCUMENT:
{context}

QUESTION: {question}

ANSWER: Provide a clear, accurate answer based only on the document above. If the document doesn't contain the answer, say so."""
            else:
                user_prompt = f"""Based on the documents provided below, answer the user's question.

DOCUMENTS:
{context}

QUESTION: {question}

ANSWER: Provide a clear, accurate answer based only on the documents above. If the documents don't contain the answer, say so."""
            
            # Call Groq API
            print(f"📤 Calling Groq API with model: {self.model}")
            response = self.groq.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            print("✅ Groq response received")
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return f"Error generating answer: {str(e)}"