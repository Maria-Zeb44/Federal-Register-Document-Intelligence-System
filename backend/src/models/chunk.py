class Chunk:
    def __init__(self, id=None, document_id=None, chunk_text=None, 
                 embedding=None, chunk_index=None):
        self.id = id
        self.document_id = document_id
        self.chunk_text = chunk_text
        self.embedding = embedding
        self.chunk_index = chunk_index