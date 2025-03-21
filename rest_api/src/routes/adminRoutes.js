/**
 * Routes for administrative endpoints.
 */
const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');

/**
 * @route   GET /api/admin/stats
 * @desc    Get search engine statistics
 * @access  Public
 */
router.get('/stats', adminController.getStats);

/**
 * @route   POST /api/admin/cache/clear
 * @desc    Clear search engine cache
 * @access  Public
 */
router.post('/cache/clear', adminController.clearCache);

/**
 * @route   GET /api/admin/health
 * @desc    Check API health
 * @access  Public
 */
router.get('/health', adminController.healthCheck);

module.exports = router;