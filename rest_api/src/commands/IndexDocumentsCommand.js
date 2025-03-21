/**
 * Command for indexing multiple documents.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class IndexDocumentsCommand extends Command {
  /**
   * Execute the index documents command.
   * 
   * @param {Object} params - Command parameters
   * @param {Array} params.documents - Array of document objects
   * @returns {Promise<Object>} - Indexing result
   */
  async execute(params) {
    if (!this.validate(params)) {
      throw new Error(this.getValidationErrors(params).join(', '));
    }

    const { documents } = params;
    logger.info(`Executing index documents command for ${documents.length} documents`);

    try {
      const result = await pythonBridge.indexDocuments(documents);
      logger.debug(`Index documents command completed with ${result.indexed_count} documents indexed`);
      return result;
    } catch (error) {
      logger.error(`Index documents command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate index documents command parameters.
   * 
   * @param {Object} params - Command parameters
   * @returns {boolean} - Validation result
   */
  validate(params) {
    return (
      params &&
      params.documents &&
      Array.isArray(params.documents) &&
      params.documents.length > 0
    );
  }

  /**
   * Get validation errors for index documents command.
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

    if (!params.documents) {
      errors.push('Documents array is required');
    } else if (!Array.isArray(params.documents)) {
      errors.push('Documents must be an array');
    } else if (params.documents.length === 0) {
      errors.push('Documents array cannot be empty');
    } else {
      // Validate each document
      params.documents.forEach((doc, index) => {
        if (!doc) {
          errors.push(`Document at index ${index} is invalid`);
          return;
        }

        if (!doc.doc_id) {
          errors.push(`Document at index ${index} is missing doc_id`);
        } else if (typeof doc.doc_id !== 'string') {
          errors.push(`Document at index ${index} has invalid doc_id type`);
        }

        if (!doc.content) {
          errors.push(`Document at index ${index} is missing content`);
        } else if (typeof doc.content !== 'string') {
          errors.push(`Document at index ${index} has invalid content type`);
        }

        if (doc.metadata !== undefined && typeof doc.metadata !== 'object') {
          errors.push(`Document at index ${index} has invalid metadata type`);
        }
      });
    }

    return errors;
  }
}

module.exports = IndexDocumentsCommand;