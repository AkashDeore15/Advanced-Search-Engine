/**
 * Logger utility for the REST API.
 */
const winston = require('winston');

// Define log format
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: ${info.message}`
  )
);

// Create logger
const logger = winston.createLogger({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  format: logFormat,
  transports: [
    // Console logger
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        logFormat
      )
    }),
    // File logger for errors
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    // File logger for all logs
    new winston.transports.File({
      filename: 'logs/combined.log'
    })
  ]
});

// Create directory for logs
const fs = require('fs');
const path = require('path');
const logDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

module.exports = logger;