/**
 * Tests for admin controller.
 */
const request = require('supertest');
const { app } = require('../src/server');
const pythonBridge = require('../src/utils/pythonBridge');

// Mock the pythonBridge
jest.mock('../src/utils/pythonBridge', () => ({
  getStats: jest.fn(),
  clearCache: jest.fn()
}));

describe('Admin Controller', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('getStats', () => {
    test('should get search engine statistics', async () => {
      // Mock the get stats result
      const mockStats = {
        num_documents: 100,
        is_index_built: true,
        ranker_type: 'TF-IDF Ranker',
        cache: {
          hits: 50,
          misses: 20,
          hit_ratio: 0.714
        }
      };

      pythonBridge.getStats.mockResolvedValue({ stats: mockStats });

      // Send request
      const response = await request(app).get('/api/admin/stats');

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('stats');
      expect(response.body.stats).toHaveProperty('num_documents', 100);
      expect(response.body.stats).toHaveProperty('ranker_type', 'TF-IDF Ranker');
      expect(response.body.stats).toHaveProperty('cache');
      expect(response.body.stats.cache).toHaveProperty('hit_ratio', 0.714);

      // Check that the getStats function was called
      expect(pythonBridge.getStats).toHaveBeenCalled();
    });

    test('should handle errors', async () => {
      // Mock the getStats function to throw an error
      pythonBridge.getStats.mockRejectedValue(new Error('Test error'));

      // Send request
      const response = await request(app).get('/api/admin/stats');

      // Check response
      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error', 'Internal Server Error');

      // Check that the getStats function was called
      expect(pythonBridge.getStats).toHaveBeenCalled();
    });
  });

  describe('clearCache', () => {
    test('should clear cache successfully', async () => {
      // Mock the clear cache result
      pythonBridge.clearCache.mockResolvedValue({ success: true });

      // Send request
      const response = await request(app).post('/api/admin/cache/clear');

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('message', 'Cache cleared successfully');

      // Check that the clearCache function was called
      expect(pythonBridge.clearCache).toHaveBeenCalled();
    });

    test('should handle cache clearing failure', async () => {
      // Mock the clear cache result
      pythonBridge.clearCache.mockResolvedValue({
        success: false,
        reason: 'Cache not enabled'
      });

      // Send request
      const response = await request(app).post('/api/admin/cache/clear');

      // Check response
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('success', false);
      expect(response.body).toHaveProperty('message', 'Cache not enabled');

      // Check that the clearCache function was called
      expect(pythonBridge.clearCache).toHaveBeenCalled();
    });
  });

  describe('healthCheck', () => {
    test('should return health status', async () => {
      // Send request
      const response = await request(app).get('/api/admin/health');

      // Check response
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('status', 'ok');
      expect(response.body).toHaveProperty('uptime');
      expect(response.body).toHaveProperty('timestamp');
    });
  });
});