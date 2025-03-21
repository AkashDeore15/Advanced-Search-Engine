/**
 * Controller for administrative endpoints.
 */
const GetStatsCommand = require('../commands/GetStatsCommand');
const ClearCacheCommand = require('../commands/ClearCacheCommand');
const logger = require('../utils/logger');

/**
 * Handle get statistics request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const getStats = async (req, res, next) => {
  try {
    // Execute get stats command
    const getStatsCommand = new GetStatsCommand();
    const result = await getStatsCommand.execute();

    // Return statistics
    res.status(200).json({
      stats: result.stats || {}
    });
  } catch (error) {
    logger.error(`Get stats failed: ${error.message}`);
    next(error);
  }
};

/**
 * Handle clear cache request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const clearCache = async (req, res, next) => {
  try {
    // Execute clear cache command
    const clearCacheCommand = new ClearCacheCommand();
    const result = await clearCacheCommand.execute();

    // Return result
    if (!result.success) {
      return res.status(400).json({
        success: false,
        message: result.reason || 'Failed to clear cache'
      });
    }

    res.status(200).json({
      success: true,
      message: 'Cache cleared successfully'
    });
  } catch (error) {
    logger.error(`Clear cache failed: ${error.message}`);
    next(error);
  }
};

/**
 * Handle health check request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const healthCheck = (req, res) => {
  res.status(200).json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
};

module.exports = {
  getStats,
  clearCache,
  healthCheck
};