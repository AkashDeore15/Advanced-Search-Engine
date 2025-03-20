"""
TF-IDF Ranker module for the Advanced Search Engine.
Implements a ranker based on TF-IDF (Term Frequency-Inverse Document Frequency).
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class TfIdfRanker:
    """
    A ranker that uses TF-IDF to rank documents based on their relevance to a query.
    """
    def __init__(self, vectorizer=None):
        """
        Initialize a new TF-IDF ranker.

        Args:
            vectorizer (TfidfVectorizer, optional): A pre-configured TF-IDF vectorizer.
                If None, the ranker will use the vectorizer from the indexer.
        """
        self.vectorizer = vectorizer
        self.name = "TF-IDF Ranker"

    def rank(self, query_vector, document_vectors):
        """
        Rank documents based on their cosine similarity to the query.

        Args:
            query_vector: The vectorized query.
            document_vectors: The vectorized documents to rank.

        Returns:
            numpy.ndarray: Array of indices sorted by relevance (most relevant first).
        """
        # Calculate cosine similarity between query and documents
        similarities = cosine_similarity(query_vector, document_vectors).flatten()
        # Return indices sorted by similarity in descending order
        return np.argsort(similarities)[::-1]

    def explain(self, query_vector, document_vector, feature_names):
        """
        Explain the ranking for a document.

        Args:
            query_vector: The vectorized query.
            document_vector: The vectorized document.
            feature_names: Array of feature names (terms).

        Returns:
            dict: Explanation of the ranking with term contributions.
        """
        # Get non-zero terms in the query
        query_terms = query_vector.nonzero()[1]
        # Get non-zero terms in the document
        doc_terms = document_vector.nonzero()[1]
        # Calculate cosine similarity
        similarity = cosine_similarity(query_vector, document_vector)[0][0]
        # Find common terms
        common_terms = np.intersect1d(query_terms, doc_terms)
        # Calculate term contributions
        contributions = []
        for term_idx in common_terms:
            term = feature_names[term_idx]
            query_weight = query_vector[0, term_idx]
            doc_weight = document_vector[0, term_idx]
            contribution = query_weight * doc_weight
            contributions.append({
                'term': term,
                'query_weight': float(query_weight),
                'doc_weight': float(doc_weight),
                'contribution': float(contribution)
            })
        # Sort by contribution (highest first)
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        return {
            'similarity': float(similarity),
            'matching_terms': len(common_terms),
            'term_contributions': contributions
        }
