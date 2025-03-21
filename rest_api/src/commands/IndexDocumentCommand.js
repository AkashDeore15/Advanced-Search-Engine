/**
 * Command for indexing a document.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class IndexDocumentCommand extends Command {
  /**
   * Execute the index document command.
   * 
   * @param {Object} params - Command parameters
   * @param {string} params.docId - Document ID
   * @param {string} params.content - Document content
   * @param {Object} params.metadata - Document metadata (optional)
   * @returns {Promise<Object>} - Indexing result
   */
  async execute(params) {
    if (!this.validate(params)) {
      throw new Error(this.getValidationErrors(params).join(', '));
    }

    const { docId, content, metadata = {} } = params;
    logger.info(`Executing index document command for document: "${docId}"`);

    try {
      const result = await pythonBridge.indexDocument(docId, content, metadata);
      logger.debug(`Index document command completed with success: ${result.success}`);
      return result;
    } catch (error) {
      logger.error(`Index document command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate index document command parameters.
   * 
   * @param {Object} params - Command parameters
   * @returns {boolean} - Validation result
   */
  validate(params) {
    return (
      params &&
      params.docId &&
      typeof params.docId === 'string' &&
      params.content &&
      typeof params.content === 'string'
    );
  }

  /**
   * Get validation errors for index document command.
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

    if (!params.docId) {
      errors.push('Document ID is required');
    } else if (typeof params.docId !== 'string') {
      errors.push('Document ID must be a string');
    }

    if (!params.content) {
      errors.push('Content is required');
    } else if (typeof params.content !== 'string') {
      errors.push('Content must be a string');
    }

    if (params.metadata !== undefined && typeof params.metadata !== 'object') {
      errors.push('Metadata must be an object');
    }

    return errors;
  }
}

module.exports = IndexDocumentCommand;