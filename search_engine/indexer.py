"""
Indexer module for the Advanced Search Engine.
Provides functionality to index documents for efficient retrieval and searching.
"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .document import Document

class Indexer:
    """
    The Indexer class is responsible for indexing documents and providing
    a way to retrieve them based on search queries using TF-IDF.
    """
    def __init__(self):
        """
        Initialize a new Indexer instance.
        """
        self.documents = {}  # Dictionary to store documents by ID
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode',
            analyzer='word',
            stop_words='english',
            max_features=10000
        )
        self.tfidf_matrix = None
        self.feature_names = None
        self.is_index_built = False

    def add_document(self, document):
        """
        Add a document to the index.

        Args:
            document (Document): The document to be added.

        Returns:
            bool: True if the document was added successfully.
        """
        # Using LBYL principle - Check if the document is an instance of Document
        if not isinstance(document, Document):
            raise TypeError("Expected document to be an instance of Document")
        # Check if a document with this ID already exists
        if document.doc_id in self.documents:
            # Document already exists, consider updating or raising an error
            return False
        # Add the document
        self.documents[document.doc_id] = document
        self.is_index_built = False  # Mark that the index needs to be rebuilt
        return True

    def add_documents(self, documents):
        """
        Add multiple documents to the index.

        Args:
            documents (list): List of Document instances to be added.

        Returns:
            int: Number of documents successfully added.
        """
        # Using EAFP principle - try to add each document and count successes
        added = 0
        for doc in documents:
            try:
                if self.add_document(doc):
                    added += 1
            except TypeError:
                # Skip invalid documents and continue
                continue
        return added

    def remove_document(self, doc_id):
        """
        Remove a document from the index.

        Args:
            doc_id (str): The ID of the document to remove.

        Returns:
            bool: True if the document was removed successfully.
        """
        # Using EAFP principle - try to remove the document
        try:
            del self.documents[doc_id]
            self.is_index_built = False  # Mark that the index needs to be rebuilt
            return True
        except KeyError:
            # Document not found
            return False

    def get_document(self, doc_id):
        """
        Retrieve a document by its ID.

        Args:
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Document: The requested document, or None if not found.
        """
        # Using EAFP principle - try to get the document
        try:
            return self.documents[doc_id]
        except KeyError:
            return None

    def build_index(self):
        """
        Build the TF-IDF index for all documents.

        Returns:
            bool: True if the index was built successfully.
        """
        if not self.documents:
            # No documents to index
            return False
        # Extract the content of all documents
        doc_ids = list(self.documents.keys())
        doc_contents = [self.documents[doc_id].content for doc_id in doc_ids]
        # Build the TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(doc_contents)
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())
        self.is_index_built = True
        return True

    def preprocess_query(self, query):
        """
        Preprocess a query string similar to how documents are processed.

        Args:
            query (str): The search query.

        Returns:
            str: The preprocessed query.
        """
        # Convert to lowercase
        query = query.lower()
        # Remove special characters
        query = re.sub(r'[^\w\s]', '', query)
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        return query

    def search(self, query, top_n=10):
        """
        Search for documents matching the query.

        Args:
            query (str): The search query.
            top_n (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            list: List of tuples (document, score) of top matching documents.
        """
        if not self.is_index_built:
            # Rebuild the index if needed
            if not self.build_index():
                # No documents to search
                return []
        # Preprocess the query
        processed_query = self.preprocess_query(query)
        # Transform the query to the TF-IDF space
        query_vector = self.vectorizer.transform([processed_query])
        # Compute cosine similarity between query and documents
        cosine_similarities = query_vector.dot(self.tfidf_matrix.T).toarray()[0]
        # Get the top N matching documents
        doc_ids = list(self.documents.keys())
        top_indices = np.argsort(cosine_similarities)[-top_n:][::-1]
        # Return only documents with non-zero similarity
        results = []
        for idx in top_indices:
            score = cosine_similarities[idx]
            if score > 0:
                doc_id = doc_ids[idx]
                results.append((self.documents[doc_id], score))
        return results

    def get_document_terms(self, doc_id):
        """
        Get the most important terms for a document.

        Args:
            doc_id (str): The ID of the document.

        Returns:
            list: List of (term, score) tuples for the most important terms.
        """
        if not self.is_index_built:
            if not self.build_index():
                return []

        try:
            # Get the index of the document
            doc_idx = list(self.documents.keys()).index(doc_id)
            # Get the TF-IDF scores for the document
            tfidf_scores = self.tfidf_matrix[doc_idx].toarray()[0]
            # Sort terms by TF-IDF score
            sorted_indices = np.argsort(tfidf_scores)[::-1]
            # Get terms with non-zero scores
            terms = []
            for idx in sorted_indices:
                score = tfidf_scores[idx]
                if score > 0:
                    term = self.feature_names[idx]
                    terms.append((term, score))
            return terms
        except (ValueError, IndexError):
            # Document not found
            return []

    def get_stats(self):
        """
        Get statistics about the index.

        Returns:
            dict: Dictionary containing index statistics.
        """
        stats = {
            'num_documents': len(self.documents),
            'is_index_built': self.is_index_built
        }
        if self.is_index_built:
            stats.update({
                'num_terms': len(self.feature_names),
                'index_shape': self.tfidf_matrix.shape
            })
        return stats
