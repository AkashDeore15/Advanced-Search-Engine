/**
 * Command for removing a document.
 */
const Command = require('./Command');
const pythonBridge = require('../utils/pythonBridge');
const logger = require('../utils/logger');

class RemoveDocumentCommand extends Command {
  /**
   * Execute the remove document command.
   * 
   * @param {Object} params - Command parameters
   * @param {string} params.docId - Document ID
   * @returns {Promise<Object>} - Removal result
   */
  async execute(params) {
    if (!this.validate(params)) {
      throw new Error(this.getValidationErrors(params).join(', '));
    }

    const { docId } = params;
    logger.info(`Executing remove document command for document: "${docId}"`);

    try {
      const result = await pythonBridge.removeDocument(docId);
      
      if (!result.success) {
        logger.debug(`Document not found for removal: ${docId}`);
      } else {
        logger.debug(`Remove document command completed successfully`);
      }
      
      return result;
    } catch (error) {
      logger.error(`Remove document command failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Validate remove document command parameters.
   * 
   * @param {Object} params - Command parameters
   * @returns {boolean} - Validation result
   */
  validate(params) {
    return params && params.docId && typeof params.docId === 'string';
  }

  /**
   * Get validation errors for remove document command.
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

module.exports = RemoveDocumentCommand;