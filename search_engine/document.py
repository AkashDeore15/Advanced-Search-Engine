"""
Document module for the Advanced Search Engine.
Provides a Document class to represent a document in the search engine.
"""

class Document:
    """
    Represents a document in the search engine.
    A document has a unique identifier, content, and optional metadata.
    """

    def __init__(self, doc_id, content, metadata=None):
        """
        Initialize a new Document instance.

        Args:
            doc_id (str): Unique identifier for the document.
            content (str): The text content of the document.
            metadata (dict, optional): Additional metadata for the document. Defaults to None.
        """
        self.doc_id = doc_id
        self.content = content
        self.metadata = metadata or {}

    def __repr__(self):
        """
        Return a string representation of the Document.

        Returns:
            str: String representation.
        """
        return f"Document(id={self.doc_id}, content_length={len(self.content)})"

    def to_dict(self):
        """
        Convert the Document instance to a dictionary.

        Returns:
            dict: Dictionary representation of the Document.
        """
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Document instance from a dictionary.

        Args:
            data (dict): Dictionary containing document data.

        Returns:
            Document: A new Document instance.
        """
        # Using EAFP principle - try to get the data and handle exceptions if keys are missing
        try:
            doc_id = data['doc_id']
            content = data['content']
            metadata = data.get('metadata', {})
            return cls(doc_id, content, metadata)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}") from e
