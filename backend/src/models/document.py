class Document:
    def __init__(self, id=None, document_number=None, title=None, abstract=None,
                 executive_order_number=None, publication_date=None, pdf_url=None,
                 html_url=None, full_text=None):
        self.id = id
        self.document_number = document_number
        self.title = title
        self.abstract = abstract
        self.executive_order_number = executive_order_number
        self.publication_date = publication_date
        self.pdf_url = pdf_url
        self.html_url = html_url
        self.full_text = full_text
    
    def to_dict(self):
        return {
            "id": self.id,
            "document_number": self.document_number,
            "title": self.title,
            "abstract": self.abstract,
            "executive_order_number": self.executive_order_number,
            "publication_date": str(self.publication_date) if self.publication_date else None,
            "pdf_url": self.pdf_url,
            "html_url": self.html_url
        }