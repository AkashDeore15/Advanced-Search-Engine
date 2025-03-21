/**
 * Routes for document-related endpoints.
 */
const express = require('express');
const router = express.Router();
const documentController = require('../controllers/documentController');

/**
 * @route   POST /api/documents
 * @desc    Index a single document
 * @access  Public
 * @body    {string} doc_id - Document ID
 * @body    {string} content - Document content
 * @body    {object} metadata - Document metadata (optional)
 */
router.post('/', documentController.indexDocument);

/**
 * @route   POST /api/documents/batch
 * @desc    Index multiple documents
 * @access  Public
 * @body    {array} documents - Array of documents
 */
router.post('/batch', documentController.indexDocuments);

/**
 * @route   GET /api/documents/:id
 * @desc    Get a document by ID
 * @access  Public
 * @param   {string} id - Document ID
 */
router.get('/:id', documentController.getDocument);

/**
 * @route   DELETE /api/documents/:id
 * @desc    Remove a document by ID
 * @access  Public
 * @param   {string} id - Document ID
 */
router.delete('/:id', documentController.removeDocument);

module.exports = router;