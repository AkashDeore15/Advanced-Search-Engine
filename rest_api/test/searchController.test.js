/**
 * Tests for search controller.
 */
const request = require('supertest');
const { app } = require('../src/server');
const pythonBridge = require('../src/utils/pythonBridge');

// Mock the pythonBridge
jest.mock('../src/utils/pythonBridge', () => ({
  search: jest.fn()
}));

describe('Search Controller', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should return search results', async () => {
    // Mock the search result
    const mockResults = [
      {
        doc_id: 'doc1',
        content: 'Test content 1',
        metadata: { author: 'Test Author 1' },
        score: 0.9
      },
      {
        doc_id: 'doc2',
        content: 'Test content 2',
        metadata: { author: 'Test Author 2' },
        score: 0.8
      }
    ];

    pythonBridge.search.mockResolvedValue({ results: mockResults });

    // Send request
    const response = await request(app)
      .get('/api/search')
      .query({ q: 'test query', limit: 10 });

    // Check response
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('query', 'test query');
    expect(response.body).toHaveProperty('limit', 10);
    expect(response.body).toHaveProperty('count', 2);
    expect(response.body).toHaveProperty('results');
    expect(response.body.results).toHaveLength(2);
    expect(response.body.results[0]).toHaveProperty('doc_id', 'doc1');

    // Check that the search function was called with correct parameters
    expect(pythonBridge.search).toHaveBeenCalledWith('test query', 10);
  });

  test('should return 400 if query is missing', async () => {
    // Send request without query
    const response = await request(app).get('/api/search');

    // Check response
    expect(response.status).toBe(400);
    expect(response.body).toHaveProperty('error', 'Bad Request');
    expect(response.body).toHaveProperty('message', 'Search query is required');

    // Check that the search function was not called
    expect(pythonBridge.search).not.toHaveBeenCalled();
  });

  test('should handle errors', async () => {
    // Mock the search function to throw an error
    pythonBridge.search.mockRejectedValue(new Error('Test error'));

    // Send request
    const response = await request(app)
      .get('/api/search')
      .query({ q: 'test query' });

    // Check response
    expect(response.status).toBe(500);
    expect(response.body).toHaveProperty('error', 'Internal Server Error');

    // Check that the search function was called
    expect(pythonBridge.search).toHaveBeenCalled();
  });
});