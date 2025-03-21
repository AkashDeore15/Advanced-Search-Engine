/**
 * Base Command class for implementing the Command Pattern.
 */
class Command {
    /**
     * Initialize a new Command.
     */
    constructor() {
      if (this.constructor === Command) {
        throw new Error('Abstract class "Command" cannot be instantiated directly');
      }
    }
  
    /**
     * Execute the command.
     * 
     * @param {Object} params - Command parameters
     * @returns {Promise<Object>} - Command result
     */
    async execute(params) {
      throw new Error('Method "execute" must be implemented');
    }
  
    /**
     * Validate parameters for the command.
     * 
     * @param {Object} params - Command parameters
     * @returns {boolean} - Validation result
     */
    validate(params) {
      return true;
    }
  
    /**
     * Get validation errors.
     * 
     * @param {Object} params - Command parameters
     * @returns {Array} - Validation errors
     */
    getValidationErrors(params) {
      return [];
    }
  }
  
  module.exports = Command;