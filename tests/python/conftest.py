# Create tests/python/conftest.py
import pytest

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
