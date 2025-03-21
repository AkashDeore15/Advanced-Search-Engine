/**
 * Controller for document-related endpoints.
 */
const IndexDocumentCommand = require('../commands/IndexDocumentCommand');
const IndexDocumentsCommand = require('../commands/IndexDocumentsCommand');
const GetDocumentCommand = require('../commands/GetDocumentCommand');
const RemoveDocumentCommand = require('../commands/RemoveDocumentCommand');
const logger = require('../utils/logger');

/**
 * Handle index document request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const indexDocument = async (req, res, next) => {
  try {
    const { doc_id, content, metadata } = req.body;

    // Validate input
    if (!doc_id) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Document ID is required'
      });
    }

    if (!content) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Document content is required'
      });
    }

    // Execute index document command
    const indexDocumentCommand = new IndexDocumentCommand();
    const result = await indexDocumentCommand.execute({
      docId: doc_id,
      content,
      metadata
    });

    // Return result
    res.status(result.success ? 200 : 400).json({
      success: result.success,
      doc_id
    });
  } catch (error) {
    logger.error(`Index document failed: ${error.message}`);
    next(error);
  }
};

/**
 * Handle index multiple documents request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const indexDocuments = async (req, res, next) => {
  try {
    const { documents } = req.body;

    // Validate input
    if (!documents || !Array.isArray(documents) || documents.length === 0) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'Documents array is required and cannot be empty'
      });
    }

    // Execute index documents command
    const indexDocumentsCommand = new IndexDocumentsCommand();
    const result = await indexDocumentsCommand.execute({ documents });

    // Return result
    res.status(200).json({
      indexed_count: result.indexed_count,
      total_count: documents.length
    });
  } catch (error) {
    logger.error(`Index documents failed: ${error.message}`);
    next(error);
  }
};

/**
 * Handle get document request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const getDocument = async (req, res, next) => {
  try {
    const docId = req.params.id;

    // Execute get document command
    const getDocumentCommand = new GetDocumentCommand();
    const result = await getDocumentCommand.execute({ docId });

    // Handle document not found
    if (result.error) {
      return res.status(result.status || 404).json({
        error: result.error,
        doc_id: docId
      });
    }

    // Return document
    res.status(200).json({
      doc_id: result.doc_id,
      content: result.content,
      metadata: result.metadata
    });
  } catch (error) {
    logger.error(`Get document failed: ${error.message}`);
    next(error);
  }
};

/**
 * Handle remove document request.
 * 
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const removeDocument = async (req, res, next) => {
  try {
    const docId = req.params.id;

    // Execute remove document command
    const removeDocumentCommand = new RemoveDocumentCommand();
    const result = await removeDocumentCommand.execute({ docId });

    // Return result
    res.status(result.success ? 200 : 404).json({
      success: result.success,
      doc_id: docId
    });
  } catch (error) {
    logger.error(`Remove document failed: ${error.message}`);
    next(error);
  }
};

module.exports = {
  indexDocument,
  indexDocuments,
  getDocument,
  removeDocument
};