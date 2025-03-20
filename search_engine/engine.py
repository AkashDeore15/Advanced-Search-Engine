"""
Engine module for the Advanced Search Engine.
Provides the main entry point for the search engine functionality.
"""
from .document import Document
from .indexer import Indexer
from .factories.ranker_factory import RankerFactory


class SearchEngine:
    """
    The main search engine class that orchestrates indexing and searching.
    """

    def __init__(self, ranker_type='tfidf'):
        """
        Initialize a new SearchEngine instance.

        Args:
            ranker_type (str, optional): The type of ranker to use. Defaults to 'tfidf'.
        """
        self.indexer = Indexer()
        self.ranker_factory = RankerFactory()
        self.ranker = self.ranker_factory.create_ranker(ranker_type)

    def index_document(self, doc_id, content, metadata=None):
        """
        Index a new document.

        Args:
            doc_id (str): Unique identifier for the document.
            content (str): The text content of the document.
            metadata (dict, optional): Additional metadata for the document. Defaults to None.

        Returns:
            bool: True if the document was indexed successfully.
        """
        doc = Document(doc_id, content, metadata)
        return self.indexer.add_document(doc)

    def index_documents(self, documents_data):
        """
        Index multiple documents.

        Args:
            documents_data (list): List of dictionaries containing document data.
                Each dictionary should have 'doc_id' and 'content' keys,
                and an optional 'metadata' key.

        Returns:
            int: Number of documents successfully indexed.
        """
        documents = []
        for data in documents_data:
            try:
                doc = Document.from_dict(data)
                documents.append(doc)
            except ValueError:
                # Skip invalid documents
                continue
        return self.indexer.add_documents(documents)

    def remove_document(self, doc_id):
        """
        Remove a document from the index.

        Args:
            doc_id (str): The ID of the document to remove.

        Returns:
            bool: True if the document was removed successfully.
        """
        return self.indexer.remove_document(doc_id)

    def get_document(self, doc_id):
        """
        Retrieve a document by its ID.

        Args:
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Document: The requested document, or None if not found.
        """
        return self.indexer.get_document(doc_id)

    def search(self, query, top_n=10):
        """
        Search for documents matching the query.

        Args:
            query (str): The search query.
            top_n (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            list: List of dictionaries containing search results.
                Each dictionary has 'doc_id', 'content', 'metadata', and 'score' keys.
        """
        # Build the index if it hasn't been built yet
        if not self.indexer.is_index_built:
            self.indexer.build_index()

        # Use the indexer to search for matching documents
        results = self.indexer.search(query, top_n)
        # Format the results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'doc_id': doc.doc_id,
                'content': doc.content,
                'metadata': doc.metadata,
                'score': float(score)
            })
        return formatted_results

    def get_stats(self):
        """
        Get statistics about the search engine.

        Returns:
            dict: Dictionary containing search engine statistics.
        """
        stats = self.indexer.get_stats()
        stats['ranker_type'] = self.ranker.name
        return stats

    def change_ranker(self, ranker_type):
        """
        Change the ranker used by the search engine.

        Args:
            ranker_type (str): The type of ranker to use.

        Returns:
            bool: True if the ranker was changed successfully.
        """
        try:
            self.ranker = self.ranker_factory.create_ranker(ranker_type)
            return True
        except ValueError:
            return False
