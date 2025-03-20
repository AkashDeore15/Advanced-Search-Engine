"""
Tests for the RankerFactory class.
"""
import pytest
from search_engine.factories.ranker_factory import RankerFactory
from search_engine.rankers.tfidf_ranker import TfIdfRanker

def test_create_ranker():
    """Test creating rankers with the factory."""
    # Create a TF-IDF ranker
    ranker = RankerFactory.create_ranker('tfidf')
    assert isinstance(ranker, TfIdfRanker)
    # Case insensitivity
    ranker = RankerFactory.create_ranker('TFIDF')
    assert isinstance(ranker, TfIdfRanker)
    # Create a ranker with additional arguments
    ranker = RankerFactory.create_ranker('tfidf', vectorizer='dummy_vectorizer')
    assert ranker.vectorizer == 'dummy_vectorizer'
    # Unsupported ranker type
    with pytest.raises(ValueError):
        RankerFactory.create_ranker('unsupported_type')


def test_get_available_rankers():
    """Test getting the list of available ranker types."""
    available_rankers = RankerFactory.get_available_rankers()
    assert 'tfidf' in available_rankers
    assert len(available_rankers) >= 1  # At least the TF-IDF ranker should be available
