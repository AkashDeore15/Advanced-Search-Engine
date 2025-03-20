"""
Tests for the SearchEngine class.
"""
import pytest
from search_engine.engine import SearchEngine

@pytest.fixture
def engine():
    """Create and return a SearchEngine instance for testing."""
    return SearchEngine()

@pytest.fixture
def sample_docs_data():
    """Create sample document data for testing."""
    return [
        {
            'doc_id': 'doc1',
            'content': 'This is a document about python programming.',
            'metadata': {'author': 'John'}
        },
        {
            'doc_id': 'doc2',
            'content': 'A guide to search engines and information retrieval.',
            'metadata': {'author': 'Alice'}
        },
        {
            'doc_id': 'doc3',
            'content': 'Advanced python techniques for data processing.',
            'metadata': {'author': 'Bob'}
        },
        {
            'doc_id': 'doc4',
            'content': 'TF-IDF is a method used in search engines to rank documents.',
            'metadata': {'author': 'Alice'}
        }
    ]


def test_engine_initialization(engine):
    """Test that a SearchEngine can be properly initialized."""
    assert engine.indexer is not None
    assert engine.ranker is not None
    assert engine.ranker_factory is not None


def test_index_document(engine):
    """Test indexing a single document."""
    # Index a document
    result = engine.index_document('doc1', 'Test document content.', {'author': 'Test'})
    assert result
    # Get the document
    doc = engine.get_document('doc1')
    assert doc is not None
    assert doc.doc_id == 'doc1'
    assert doc.content == 'Test document content.'
    assert doc.metadata == {'author': 'Test'}


def test_index_documents(engine, sample_docs_data):
    """Test indexing multiple documents."""
    # Index the documents
    count = engine.index_documents(sample_docs_data)
    assert count == 4
    # Try with some invalid data
    invalid_data = [
        {},  # Missing required fields
        {'content': 'Missing doc_id'},  # Missing doc_id
        {'doc_id': 'Missing content'}  # Missing content
    ]
    count = engine.index_documents(invalid_data)
    assert count == 0


def test_remove_document(engine):
    """Test removing a document."""
    # Index a document first
    engine.index_document('doc1', 'Test document content.')
    # Remove the document
    result = engine.remove_document('doc1')
    assert result
    # Try to remove a non-existent document
    result = engine.remove_document('nonexistent')
    assert not result


def test_get_document(engine):
    """Test retrieving a document."""
    # Index a document first
    engine.index_document('doc1', 'Test document content.')
    # Get the document
    doc = engine.get_document('doc1')
    assert doc is not None
    assert doc.doc_id == 'doc1'
    # Try to get a non-existent document
    doc = engine.get_document('nonexistent')
    assert doc is None


def test_search(engine, sample_docs_data):
    """Test searching for documents."""
    # Index some documents first
    engine.index_documents(sample_docs_data)
    # Search for a query
    results = engine.search('python programming')
    # We should get results
    assert len(results) > 0
    # Check the structure of the results
    first_result = results[0]
    assert 'doc_id' in first_result
    assert 'content' in first_result
    assert 'metadata' in first_result
    assert 'score' in first_result
    # The most relevant document should be doc1 or doc3 (containing "python programming")
    assert first_result['doc_id'] in ['doc1', 'doc3']
    # Search with a limit
    results = engine.search('search engines', top_n=2)
    assert len(results) <= 2


def test_get_stats(engine, sample_docs_data):
    """Test retrieving statistics about the search engine."""
    # Initially with no documents
    stats = engine.get_stats()
    assert stats['num_documents'] == 0
    assert not stats['is_index_built']
    assert 'ranker_type' in stats
    # Add documents
    engine.index_documents(sample_docs_data)
    # Check stats with documents
    stats = engine.get_stats()
    assert stats['num_documents'] == 4


def test_change_ranker(engine):
    """Test changing the ranker used by the search engine."""
    # Change to TF-IDF (should succeed even though it's already TF-IDF)
    result = engine.change_ranker('tfidf')
    assert result
    # Change to an unsupported ranker
    result = engine.change_ranker('unsupported')
    assert not result
