/**
 * Routes for search-related endpoints.
 */
const express = require('express');
const router = express.Router();
const searchController = require('../controllers/searchController');

/**
 * @route   GET /api/search
 * @desc    Search for documents
 * @access  Public
 * @query   {string} q - Search query
 * @query   {number} limit - Maximum number of results (optional)
 */
router.get('/', searchController.searchDocuments);

module.exports = router;