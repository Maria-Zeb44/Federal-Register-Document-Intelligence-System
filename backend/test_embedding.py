from src.services.embedding_service import get_embedding_service
import time

def test_embedding():
    print("🚀 Testing Embedding Service...")
    
    # Get the service (will load model on first call)
    start = time.time()
    service = get_embedding_service()
    print(f"✅ Model loaded in {time.time() - start:.2f}s")
    print(f"📊 Dimension: {service.get_dimension()}")
    
    # Test embeddings
    texts = [
        "This is a test sentence.",
        "The Federal Register publishes Executive Orders.",
        "Executive Order 14417 establishes the President's Military Spouse Commission."
    ]
    
    start = time.time()
    embeddings = service.generate_embeddings(texts)
    print(f"✅ Generated {len(embeddings)} embeddings in {time.time() - start:.2f}s")
    print(f"📊 Embedding shape: {len(embeddings)} x {len(embeddings[0])}")
    
    # Check similarity
    import numpy as np
    emb1 = np.array(embeddings[0])
    emb2 = np.array(embeddings[1])
    emb3 = np.array(embeddings[2])
    
    sim12 = np.dot(emb1, emb2)
    sim13 = np.dot(emb1, emb3)
    
    print(f"📊 Similarity (text1 vs text2): {sim12:.4f}")
    print(f"📊 Similarity (text1 vs text3): {sim13:.4f}")

if __name__ == "__main__":
    test_embedding()