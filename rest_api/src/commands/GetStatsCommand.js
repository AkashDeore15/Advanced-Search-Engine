/**
 * Command for retrieving search engine statistics.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class GetStatsCommand extends Command {
  /**
   * Execute the get stats command.
   * 
   * @param {Object} params - Command parameters (optional)
   * @returns {Promise<Object>} - Statistics data
   */
  async execute(params = {}) {
    logger.info('Executing get stats command');

    try {
      const result = await pythonBridge.getStats();
      logger.debug('Get stats command completed successfully');
      return result;
    } catch (error) {
      logger.error(`Get stats command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate get stats command parameters.
   * This command doesn't require any parameters.
   * 
   * @returns {boolean} - Always returns true
   */
  validate() {
    return true;
  }

  /**
   * Get validation errors for get stats command.
   * This command doesn't require any parameters.
   * 
   * @returns {Array} - Empty array (no validation errors)
   */
  getValidationErrors() {
    return [];
  }
}

module.exports = GetStatsCommand;