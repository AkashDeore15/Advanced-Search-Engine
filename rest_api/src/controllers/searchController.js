/**
 * Controller for search-related endpoints.
 */
const SearchCommand = require('../commands/SearchCommand');
const logger = require('../utils/logger');

/**
 * Handle search request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const searchDocuments = async (req, res, next) => {
  try {
    const query = req.query.q || '';
    const limit = req.query.limit ? parseInt(req.query.limit, 10) : 10;

    // Validate input
    if (!query) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Search query is required'
      });
    }

    // Execute search command
    const searchCommand = new SearchCommand();
    const result = await searchCommand.execute({ query, limit });

    // Return search results
    res.status(200).json({
      query,
      limit,
      count: result.results ? result.results.length : 0,
      results: result.results || []
    });
  } catch (error) {
    logger.error(`Search failed: ${error.message}`);
    next(error);
  }
};

module.exports = {
  searchDocuments
};