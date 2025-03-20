"""
Tests for the TfIdfRanker class.
"""
import pytest
import numpy as np
from scipy.sparse import csr_matrix
from search_engine.rankers.tfidf_ranker import TfIdfRanker

@pytest.fixture
def ranker():
    """Create and return a TfIdfRanker instance for testing."""
    return TfIdfRanker()


@pytest.fixture
def sample_data():
    """Create sample vectors and feature names for testing."""
    # Create a simple query vector (1 query, 5 features)
    query_vector = csr_matrix([[0.5, 0.0, 0.8, 0.0, 0.3]])
    # Create document vectors (3 documents, 5 features)
    document_vectors = csr_matrix([
        [0.2, 0.3, 0.4, 0.1, 0.0],  # doc1
        [0.0, 0.1, 0.0, 0.7, 0.2],  # doc2
        [0.6, 0.0, 0.7, 0.0, 0.1]   # doc3
    ])
    # Feature names
    feature_names = np.array(['term1', 'term2', 'term3', 'term4', 'term5'])
    return {
        'query_vector': query_vector,
        'document_vectors': document_vectors,
        'feature_names': feature_names
    }


def test_ranker_initialization(ranker):
    """Test that a TfIdfRanker can be properly initialized."""
    assert ranker.name == "TF-IDF Ranker"
    assert ranker.vectorizer is None


def test_rank(ranker, sample_data):
    """Test ranking documents based on query similarity."""
    # Rank the documents
    ranked_indices = ranker.rank(
        sample_data['query_vector'],
        sample_data['document_vectors']
    )
    # The ranking should be: doc3, doc1, doc2
    # doc3 has high scores for terms 1 and 3 which are in the query
    # doc1 has medium scores for terms 1 and 3
    # doc2 has no significant terms matching the query
    assert ranked_indices[0] == 2  # doc3
    assert ranked_indices[1] == 0  # doc1
    assert ranked_indices[2] == 1  # doc2


def test_explain(ranker, sample_data):
    """Test explanation of ranking for a document."""
    # Get explanation for doc3
    explanation = ranker.explain(
        sample_data['query_vector'],
        sample_data['document_vectors'][2].reshape(1, -1),
        sample_data['feature_names']
    )
    # Check the similarity score
    assert 'similarity' in explanation
    assert explanation['similarity'] > 0.9  # doc3 is highly similar to the query
    # Check matching terms
    assert explanation['matching_terms'] == 3  # term1, term3, term5
    # Check term contributions
    assert 'term_contributions' in explanation
    assert len(explanation['term_contributions']) > 0
    # The highest contributing term should be term3
    assert explanation['term_contributions'][0]['term'] == 'term3'
    # All contributions should be positive
    for contrib in explanation['term_contributions']:
        assert contrib['contribution'] > 0
