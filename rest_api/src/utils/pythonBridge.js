/**
 * Python bridge for interacting with the Python search engine.
 */
const { spawn } = require('child_process');
const path = require('path');
const logger = require('./logger');

class PythonBridge {
  constructor() {
    this.pythonExecutable = process.env.PYTHON_EXECUTABLE || 'python';
    this.searchEnginePath = process.env.SEARCH_ENGINE_PATH || '../search_engine';
    this.bridgeScriptPath = path.join(__dirname, 'bridge_script.py');
  }

  /**
   * Execute a command on the Python search engine.
   * 
   * @param {string} command - The command to execute
   * @param {Object} params - Parameters for the command
   * @returns {Promise<Object>} - Command result
   */
  executeCommand(command, params = {}) {
    return new Promise((resolve, reject) => {
      // Execute the Python script
      const pythonProcess = spawn(this.pythonExecutable, [
        this.bridgeScriptPath,
        command,
        JSON.stringify(params)
      ]);

      let dataString = '';
      let errorString = '';

      // Collect data from stdout
      pythonProcess.stdout.on('data', (data) => {
        dataString += data.toString();
      });

      // Collect errors from stderr
      pythonProcess.stderr.on('data', (data) => {
        errorString += data.toString();
      });

      // Handle process completion
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          logger.error(`Python process exited with code ${code}: ${errorString}`);
          reject(new Error(`Python process failed: ${errorString}`));
          return;
        }

        // Parse the JSON result
        try {
          const result = JSON.parse(dataString);
          resolve(result);
        } catch (error) {
          logger.error(`Failed to parse Python output: ${error.message}`);
          reject(new Error(`Failed to parse Python output: ${error.message}`));
        }
      });

      // Handle process errors
      pythonProcess.on('error', (error) => {
        logger.error(`Failed to start Python process: ${error.message}`);
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  }

  /**
   * Search for documents.
   * 
   * @param {string} query - The search query
   * @param {number} topN - Maximum number of results
   * @returns {Promise<Array>} - Search results
   */
  search(query, topN = 10) {
    return this.executeCommand('search', { query, top_n: topN });
  }

  /**
   * Index a document.
   * 
   * @param {string} docId - Document ID
   * @param {string} content - Document content
   * @param {Object} metadata - Document metadata
   * @returns {Promise<Object>} - Indexing result
   */
  indexDocument(docId, content, metadata = {}) {
    return this.executeCommand('index_document', {
      doc_id: docId,
      content,
      metadata
    });
  }

  /**
   * Index multiple documents.
   * 
   * @param {Array} documents - Array of document objects
   * @returns {Promise<Object>} - Indexing result
   */
  indexDocuments(documents) {
    return this.executeCommand('index_documents', { documents });
  }

  /**
   * Remove a document.
   * 
   * @param {string} docId - Document ID
   * @returns {Promise<Object>} - Removal result
   */
  removeDocument(docId) {
    return this.executeCommand('remove_document', { doc_id: docId });
  }

  /**
   * Get a document by ID.
   * 
   * @param {string} docId - Document ID
   * @returns {Promise<Object>} - Document data
   */
  getDocument(docId) {
    return this.executeCommand('get_document', { doc_id: docId });
  }

  /**
   * Get search engine statistics.
   * 
   * @returns {Promise<Object>} - Statistics data
   */
  getStats() {
    return this.executeCommand('get_stats');
  }

  /**
   * Clear cache.
   * 
   * @returns {Promise<Object>} - Clear cache result
   */
  clearCache() {
    return this.executeCommand('clear_cache');
  }
}

// Export singleton instance
module.exports = new PythonBridge();