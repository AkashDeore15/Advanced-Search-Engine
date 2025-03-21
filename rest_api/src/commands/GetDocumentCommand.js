/**
 * Command for retrieving a document.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class GetDocumentCommand extends Command {
  /**
   * Execute the get document command.
   * 
   * @param {Object} params - Command parameters
   * @param {string} params.docId - Document ID
   * @returns {Promise<Object>} - Document data
   */
  async execute(params) {
    if (!this.validate(params)) {
      throw new Error(this.getValidationErrors(params).join(', '));
    }

    const { docId } = params;
    logger.info(`Executing get document command for document: "${docId}"`);

    try {
      const result = await pythonBridge.getDocument(docId);
      
      if (result.error) {
        logger.debug(`Document not found: ${docId}`);
        return { error: 'Document not found', status: 404 };
      }
      
      logger.debug(`Get document command completed successfully`);
      return result;
    } catch (error) {
      logger.error(`Get document command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate get document command parameters.
   * 
   * @param {Object} params - Command parameters
   * @returns {boolean} - Validation result
   */
  validate(params) {
    return params && params.docId && typeof params.docId === 'string';
  }

  /**
   * Get validation errors for get document command.
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

    return errors;
  }
}

module.exports = GetDocumentCommand;