"""
Tests for the Document class.
"""
import pytest
from search_engine.document import Document


def test_document_initialization():
    """Test that a Document can be properly initialized."""
    doc = Document("doc1", "This is a test document.")
    assert doc.doc_id == "doc1"
    assert doc.content == "This is a test document."
    assert doc.metadata == {}


def test_document_with_metadata():
    """Test that a Document can be initialized with metadata."""
    metadata = {"author": "John Doe", "date": "2023-03-15"}
    doc = Document("doc2", "Another test document.", metadata)
    assert doc.doc_id == "doc2"
    assert doc.content == "Another test document."
    assert doc.metadata == metadata


def test_document_to_dict():
    """Test that a Document can be converted to a dictionary."""
    metadata = {"author": "Jane Smith"}
    doc = Document("doc3", "Document for testing to_dict method.", metadata)
    doc_dict = doc.to_dict()
    assert doc_dict["doc_id"] == "doc3"
    assert doc_dict["content"] == "Document for testing to_dict method."
    assert doc_dict["metadata"] == metadata


def test_document_from_dict():
    """Test that a Document can be created from a dictionary."""
    doc_dict = {
        "doc_id": "doc4",
        "content": "Document for testing from_dict method.",
        "metadata": {"author": "Alice Johnson"}
    }
    doc = Document.from_dict(doc_dict)
    assert doc.doc_id == "doc4"
    assert doc.content == "Document for testing from_dict method."
    assert doc.metadata == {"author": "Alice Johnson"}


def test_document_from_dict_missing_fields():
    """Test that from_dict raises ValueError when required fields are missing."""
    # Missing doc_id
    doc_dict = {
        "content": "Document missing doc_id field."
    }
    with pytest.raises(ValueError):
        Document.from_dict(doc_dict)
    # Missing content
    doc_dict = {
        "doc_id": "doc5"
    }
    with pytest.raises(ValueError):
        Document.from_dict(doc_dict)

def test_document_representation():
    """Test the string representation of a Document."""
    # Create a document with a known content length
    doc = Document("doc6", "Document for testing __repr__ method.")
    # The representation should include the document ID and content length
    assert "doc6" in repr(doc)
    assert "37" in repr(doc)  # Actual length of the content string
