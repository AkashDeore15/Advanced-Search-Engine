/**
 * Tests for document controller.
 */
const request = require('supertest');
const { app } = require('../src/server');
const pythonBridge = require('../src/utils/pythonBridge');

// Mock the pythonBridge
jest.mock('../src/utils/pythonBridge', () => ({
  indexDocument: jest.fn(),
  indexDocuments: jest.fn(),
  getDocument: jest.fn(),
  removeDocument: jest.fn()
}));

describe('Document Controller', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('indexDocument', () => {
    test('should index a document', async () => {
      // Mock the index document result
      pythonBridge.indexDocument.mockResolvedValue({ success: true });

      // Send request
      const response = await request(app)
        .post('/api/documents')
        .send({
          doc_id: 'test-doc',
          content: 'Test content',
          metadata: { author: 'Test Author' }
        });

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('doc_id', 'test-doc');

      // Check that the indexDocument function was called with correct parameters
      expect(pythonBridge.indexDocument).toHaveBeenCalledWith(
        'test-doc',
        'Test content',
        { author: 'Test Author' }
      );
    });

    test('should return 400 if doc_id is missing', async () => {
      // Send request without doc_id
      const response = await request(app)
        .post('/api/documents')
        .send({
          content: 'Test content'
        });

      // Check response
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error', 'Bad Request');
      expect(response.body).toHaveProperty('message', 'Document ID is required');

      // Check that the indexDocument function was not called
      expect(pythonBridge.indexDocument).not.toHaveBeenCalled();
    });
  });

  describe('getDocument', () => {
    test('should get a document', async () => {
      // Mock the get document result
      pythonBridge.getDocument.mockResolvedValue({
        doc_id: 'test-doc',
        content: 'Test content',
        metadata: { author: 'Test Author' }
      });

      // Send request
      const response = await request(app).get('/api/documents/test-doc');

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('doc_id', 'test-doc');
      expect(response.body).toHaveProperty('content', 'Test content');
      expect(response.body).toHaveProperty('metadata');
      expect(response.body.metadata).toHaveProperty('author', 'Test Author');

      // Check that the getDocument function was called with correct parameters
      expect(pythonBridge.getDocument).toHaveBeenCalledWith('test-doc');
    });

    test('should return 404 if document not found', async () => {
      // Mock the get document result
      pythonBridge.getDocument.mockResolvedValue({
        error: 'Document not found'
      });

      // Send request
      const response = await request(app).get('/api/documents/nonexistent');

      // Check response
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error', 'Document not found');
      expect(response.body).toHaveProperty('doc_id', 'nonexistent');

      // Check that the getDocument function was called
      expect(pythonBridge.getDocument).toHaveBeenCalledWith('nonexistent');
    });
  });

  describe('removeDocument', () => {
    test('should remove a document', async () => {
      // Mock the remove document result
      pythonBridge.removeDocument.mockResolvedValue({ success: true });

      // Send request
      const response = await request(app).delete('/api/documents/test-doc');

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('doc_id', 'test-doc');

      // Check that the removeDocument function was called with correct parameters
      expect(pythonBridge.removeDocument).toHaveBeenCalledWith('test-doc');
    });

    test('should return 404 if document not found', async () => {
      // Mock the remove document result
      pythonBridge.removeDocument.mockResolvedValue({ success: false });

      // Send request
      const response = await request(app).delete('/api/documents/nonexistent');

      // Check response
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('success', false);
      expect(response.body).toHaveProperty('doc_id', 'nonexistent');

      // Check that the removeDocument function was called
      expect(pythonBridge.removeDocument).toHaveBeenCalledWith('nonexistent');
    });
  });

  describe('indexDocuments', () => {
    test('should index multiple documents', async () => {
      // Mock the index documents result
      pythonBridge.indexDocuments.mockResolvedValue({ indexed_count: 2 });

      // Sample documents
      const documents = [
        {
          doc_id: 'doc1',
          content: 'Test content 1',
          metadata: { author: 'Author 1' }
        },
        {
          doc_id: 'doc2',
          content: 'Test content 2',
          metadata: { author: 'Author 2' }
        }
      ];

      // Send request
      const response = await request(app)
        .post('/api/documents/batch')
        .send({ documents });

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('indexed_count', 2);
      expect(response.body).toHaveProperty('total_count', 2);

      // Check that the indexDocuments function was called with correct parameters
      expect(pythonBridge.indexDocuments).toHaveBeenCalledWith(documents);
    });

    test('should return 400 if documents array is missing', async () => {
      // Send request without documents
      const response = await request(app)
        .post('/api/documents/batch')
        .send({});

      // Check response
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error', 'Bad Request');
      expect(response.body).toHaveProperty('message', 'Documents array is required and cannot be empty');

      // Check that the indexDocuments function was not called
      expect(pythonBridge.indexDocuments).not.toHaveBeenCalled();
    });
  });
});