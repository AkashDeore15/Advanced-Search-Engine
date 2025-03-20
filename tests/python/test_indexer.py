"""
Tests for the Indexer class.
"""
import pytest
from search_engine.document import Document
from search_engine.indexer import Indexer


@pytest.fixture
def indexer():
    """Create and return an Indexer instance for testing."""
    return Indexer()


@pytest.fixture
def sample_documents():
    """Create and return a list of sample documents for testing."""
    return [
        Document("doc1", "This is the first test document about search engines."),
        Document("doc2", "A second document discussing indexing and searching."),
        Document("doc3", "The third document covers ranking algorithms."),
        Document("doc4", "Document number four talks about TF-IDF and search relevance.")
    ]


def test_indexer_initialization(indexer):
    """Test that an Indexer can be properly initialized."""
    assert indexer.documents == {}
    assert not indexer.is_index_built
    assert indexer.tfidf_matrix is None
    assert indexer.feature_names is None


def test_add_document(indexer):
    """Test adding a document to the Indexer."""
    doc = Document("doc1", "Test document content.")
    # Adding a new document should succeed
    assert indexer.add_document(doc)
    assert "doc1" in indexer.documents
    assert not indexer.is_index_built
    # Adding a document with an existing ID should fail
    assert not indexer.add_document(doc)


def test_add_document_type_check(indexer):
    """Test that add_document checks the type of the document."""
    # Trying to add something other than a Document should raise TypeError
    with pytest.raises(TypeError):
        indexer.add_document("not a document")


def test_add_documents(indexer, sample_documents):
    """Test adding multiple documents to the Indexer."""
    # All sample documents should be added successfully
    assert indexer.add_documents(sample_documents) == 4
    # Now try adding a mix of valid and invalid documents
    mixed_docs = [
        Document("doc5", "Another valid document."),
        "not a document",  # Invalid
        Document("doc1", "This ID already exists.")  # Already exists
    ]
    # Only the new valid document should be added
    assert indexer.add_documents(mixed_docs) == 1
    assert len(indexer.documents) == 5


def test_remove_document(indexer, sample_documents):
    """Test removing a document from the Indexer."""
    # Add some documents first
    indexer.add_documents(sample_documents)
    # Removing an existing document should succeed
    assert indexer.remove_document("doc2")
    assert "doc2" not in indexer.documents
    assert not indexer.is_index_built
    # Removing a non-existent document should fail
    assert not indexer.remove_document("nonexistent")


def test_get_document(indexer, sample_documents):
    """Test retrieving a document from the Indexer."""
    # Add some documents first
    indexer.add_documents(sample_documents)
    # Getting an existing document should work
    doc = indexer.get_document("doc3")
    assert doc is not None
    assert doc.doc_id == "doc3"
    # Getting a non-existent document should return None
    assert indexer.get_document("nonexistent") is None


def test_build_index(indexer, sample_documents):
    """Test building the TF-IDF index."""
    # Adding documents and building the index
    indexer.add_documents(sample_documents)
    assert indexer.build_index()
    assert indexer.is_index_built
    assert indexer.tfidf_matrix is not None
    assert indexer.feature_names is not None
    # Check the dimensions of the TF-IDF matrix
    assert indexer.tfidf_matrix.shape[0] == 4  # Number of documents
    # Build index with no documents
    empty_indexer = Indexer()
    assert not empty_indexer.build_index()


def test_search(indexer, sample_documents):
    """Test searching for documents."""
    # Add documents and build the index
    indexer.add_documents(sample_documents)
    indexer.build_index()
    # Search for a query
    results = indexer.search("search engines")
    # We should get results
    assert len(results) > 0
    # The first document should be the most relevant
    assert results[0][0].doc_id == "doc1"  # Contains "search engines"
    # Check that search works when index is not built
    indexer.is_index_built = False
    results = indexer.search("ranking")
    assert len(results) > 0
    assert results[0][0].doc_id == "doc3"  # Contains "ranking"


def test_search_with_no_results(indexer):
    """Test searching for documents with no matches."""
    # Add a document and build the index
    doc = Document("doc1", "This is a test document.")
    indexer.add_document(doc)
    indexer.build_index()
    # Search for a query with no matches
    results = indexer.search("nonexistent term")
    assert len(results) == 0


def test_preprocess_query(indexer):
    """Test query preprocessing."""
    # Test basic preprocessing
    query = "Search Engines!"
    processed = indexer.preprocess_query(query)
    assert processed == "search engines"
    # Test with special characters and extra whitespace
    query = "  TF-IDF   ranking  @#$  "
    processed = indexer.preprocess_query(query)
    assert processed == "tfidf ranking"


def test_get_document_terms(indexer, sample_documents):
    """Test retrieving important terms for a document."""
    # Add documents and build the index
    indexer.add_documents(sample_documents)
    indexer.build_index()
    # Get terms for a document
    terms = indexer.get_document_terms("doc4")
    # Should return some terms
    assert len(terms) > 0
    # First term should be the most important
    assert terms[0][0] in ["tfidf", "relevance", "tf", "idf"]
    # Test with non-existent document
    terms = indexer.get_document_terms("nonexistent")
    assert terms == []
    # Test when index is not built
    indexer.is_index_built = False
    terms = indexer.get_document_terms("doc1")
    assert len(terms) > 0


def test_get_stats(indexer, sample_documents):
    """Test retrieving statistics about the index."""
    # Initially with no documents
    stats = indexer.get_stats()
    assert stats["num_documents"] == 0
    assert not stats["is_index_built"]
    # Add documents and build the index
    indexer.add_documents(sample_documents)
    indexer.build_index()
    # Check stats with documents and built index
    stats = indexer.get_stats()
    assert stats["num_documents"] == 4
    assert stats["is_index_built"]
    assert "num_terms" in stats
    assert "index_shape" in stats
