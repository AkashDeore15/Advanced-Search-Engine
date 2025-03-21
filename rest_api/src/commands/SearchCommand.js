/**
 * Command for searching documents.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class SearchCommand extends Command {
  /**
   * Execute the search command.
   * 
   * @param {Object} params - Command parameters
   * @param {string} params.query - Search query
   * @param {number} params.limit - Maximum number of results (optional)
   * @returns {Promise<Object>} - Search results
   */
  async execute(params) {
    if (!this.validate(params)) {
      throw new Error(this.getValidationErrors(params).join(', '));
    }

    const { query, limit = 10 } = params;
    logger.info(`Executing search command for query: "${query}" with limit: ${limit}`);

    try {
      const result = await pythonBridge.search(query, limit);
      logger.debug(`Search command completed with ${result.results ? result.results.length : 0} results`);
      return result;
    } catch (error) {
      logger.error(`Search command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate search command parameters.
   * 
   * @param {Object} params - Command parameters
   * @returns {boolean} - Validation result
   */
  validate(params) {
    return params && params.query && typeof params.query === 'string';
  }

  /**
   * Get validation errors for search command.
   * 
   * @param {Object} params - Command parameters
   * @returns {Array} - Validation errors
   */
  getValidationErrors(params) {
    const errors = [];

    if (!params) {
      errors.push('Parameters are required');
      return errors;
    }

    if (!params.query) {
      errors.push('Query is required');
    } else if (typeof params.query !== 'string') {
      errors.push('Query must be a string');
    }

    if (params.limit !== undefined) {
      if (typeof params.limit !== 'number') {
        errors.push('Limit must be a number');
      } else if (params.limit <= 0) {
        errors.push('Limit must be greater than 0');
      }
    }

    return errors;
  }
}

module.exports = SearchCommand;