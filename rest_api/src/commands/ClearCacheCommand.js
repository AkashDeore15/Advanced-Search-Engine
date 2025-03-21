/**
 * Command for clearing the search engine cache.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class ClearCacheCommand extends Command {
  /**
   * Execute the clear cache command.
   * 
   * @param {Object} params - Command parameters (optional)
   * @returns {Promise<Object>} - Clear cache result
   */
  async execute(params = {}) {
    logger.info('Executing clear cache command');

    try {
      const result = await pythonBridge.clearCache();
      
      if (!result.success) {
        logger.debug(`Cache clearing failed: ${result.reason || 'Unknown reason'}`);
      } else {
        logger.debug('Clear cache command completed successfully');
      }
      
      return result;
    } catch (error) {
      logger.error(`Clear cache command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate clear cache command parameters.
   * This command doesn't require any parameters.
   * 
   * @returns {boolean} - Always returns true
   */
  validate() {
    return true;
  }

  /**
   * Get validation errors for clear cache command.
   * This command doesn't require any parameters.
   * 
   * @returns {Array} - Empty array (no validation errors)
   */
  getValidationErrors() {
    return [];
  }
}

module.exports = ClearCacheCommand;