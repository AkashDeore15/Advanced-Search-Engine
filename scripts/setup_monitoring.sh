#!/bin/bash
# Script to set up monitoring with Prometheus and Grafana

# Create directories
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana

# Create Prometheus configuration
cat > monitoring/prometheus/prometheus.yml << EOL
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  
  - job_name: 'rest-api'
    metrics_path: '/api/admin/metrics'
    static_configs:
      - targets: ['rest-api:3000']
EOL

# Create Docker Compose file for monitoring
cat > monitoring/docker-compose.yml << EOL
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - '9090:9090'
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring-network
      - search-engine-network

  grafana:
    image: grafana/grafana
    ports:
      - '3001:3000'
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
    networks:
      - monitoring-network
      - search-engine-network

  node-exporter:
    image: prom/node-exporter
    ports:
      - '9100:9100'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring-network:
    driver: bridge
  search-engine-network:
    external: true
EOL

# Add metrics support to the REST API
mkdir -p rest_api/src/middleware

cat > rest_api/src/middleware/metrics.js << EOL
/**
 * Prometheus metrics middleware for Express.
 */
const prometheus = require('prom-client');
const logger = require('../utils/logger');

// Create a Registry to register the metrics
const register = new prometheus.Registry();
prometheus.collectDefaultMetrics({ register });

// Create custom metrics
const httpRequestDurationMicroseconds = new prometheus.Histogram({
  name: 'http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
});

const httpRequestsTotalByRoute = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestsErrorsByRoute = new prometheus.Counter({
  name: 'http_requests_errors_total',
  help: 'Total number of HTTP request errors',
  labelNames: ['method', 'route', 'status_code']
});

const cacheHitCounter = new prometheus.Counter({
  name: 'cache_hits_total',
  help: 'Total number of cache hits'
});

const cacheMissCounter = new prometheus.Counter({
  name: 'cache_misses_total',
  help: 'Total number of cache misses'
});

const searchDurationHistogram = new prometheus.Histogram({
  name: 'search_duration_ms',
  help: 'Duration of search operations in ms',
  buckets: [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
});

// Register custom metrics
register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestsTotalByRoute);
register.registerMetric(httpRequestsErrorsByRoute);
register.registerMetric(cacheHitCounter);
register.registerMetric(cacheMissCounter);
register.registerMetric(searchDurationHistogram);

/**
 * Express middleware to collect metrics for each request.
 */
function metricsMiddleware(req, res, next) {
  // Start time
  const startTime = Date.now();
  
  // Record metrics when response is finished
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    const route = req.route ? req.baseUrl + req.route.path : req.originalUrl;
    const method = req.method;
    const statusCode = res.statusCode;
    
    // Record request metrics
    httpRequestDurationMicroseconds.observe({ method, route, status_code: statusCode }, duration);
    httpRequestsTotalByRoute.inc({ method, route, status_code: statusCode });
    
    // Record error metrics
    if (statusCode >= 400) {
      httpRequestsErrorsByRoute.inc({ method, route, status_code: statusCode });
    }
    
    // Log for debugging
    logger.debug(`${method} ${route} ${statusCode} took ${duration}ms`);
  });
  
  next();
}

/**
 * Update cache metrics based on cache hits and misses.
 */
function updateCacheMetrics(hit) {
  if (hit) {
    cacheHitCounter.inc();
  } else {
    cacheMissCounter.inc();
  }
}

/**
 * Record search duration.
 */
function recordSearchDuration(duration) {
  searchDurationHistogram.observe(duration);
}

/**
 * Metrics endpoint handler.
 */
function metricsEndpoint(req, res) {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
}

module.exports = {
  middleware: metricsMiddleware,
  updateCacheMetrics,
  recordSearchDuration,
  metricsEndpoint
};
EOL

# Update package.json to include prometheus client
cat >> rest_api/package.json << EOL

  "dependencies": {
    "prom-client": "^14.2.0"
  }
EOL

echo "Monitoring setup completed. Run 'cd monitoring && docker-compose up -d' to start monitoring."
echo "Grafana will be available at http://localhost:3001 (admin/admin)"
echo "Prometheus will be available at http://localhost:9090"
