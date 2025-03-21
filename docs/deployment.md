# Deployment Guide for Advanced Search Engine

This guide provides instructions for deploying the Advanced Search Engine to various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have the following prerequisites:

- Docker and Docker Compose installed
- Git (for version control)
- Node.js 14+ (for local development)
- Python 3.9+ (for local development)
- Redis server (if not using Docker)

## Development Deployment

For local development, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/username/advanced-search-engine.git
   cd advanced-search-engine
   ```

2. Install dependencies:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   cd rest_api
   npm install
   cd ..
   ```

3. Start Redis:
   ```bash
   # Option 1: Use your existing Redis server
   # Make sure it's running on localhost:6379 or update the .env file
   
   # Option 2: Start Redis in Docker
   docker run --name redis -p 6379:6379 -d redis:alpine
   ```

4. Start the REST API:
   ```bash
   cd rest_api
   npm run dev
   ```

5. Test the API:
   ```bash
   curl http://localhost:3000/api/admin/health
   ```

## Production Deployment

For production deployment using Docker Compose:

1. Clone the repository:
   ```bash
   git clone https://github.com/username/advanced-search-engine.git
   cd advanced-search-engine
   ```

2. Configure environment settings:
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit the .env file with your production settings
   nano .env
   ```

3. (Optional) Generate SSL certificates:
   ```bash
   # For production, use proper SSL certificates from a trusted CA
   # For testing, generate self-signed certificates
   bash scripts/generate-ssl.sh
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. Verify deployment:
   ```bash
   # Check container status
   docker-compose ps
   
   # Check logs
   docker-compose logs -f
   
   # Test the API
   curl http://localhost/api/admin/health
   ```

## Monitoring Setup

To enable monitoring with Prometheus and Grafana:

1. Set up the monitoring stack:
   ```bash
   bash scripts/setup_monitoring.sh
   ```

2. Start the monitoring services:
   ```bash
   cd monitoring
   docker-compose up -d
   ```

3. Access the monitoring dashboards:
   - Grafana: http://localhost:3001 (default credentials: admin/admin)
   - Prometheus: http://localhost:9090

## Backup and Restore

### Backing up Redis data

Redis data can be backed up using the following methods:

1. Using RDB snapshots:
   ```bash
   # Connect to Redis container
   docker exec -it advanced-search-engine_redis_1 redis-cli
   
   # Trigger RDB snapshot
   SAVE
   
   # Exit Redis CLI
   exit
   
   # Copy the dump.rdb file from the container
   docker cp advanced-search-engine_redis_1:/data/dump.rdb ./backups/dump.rdb
   ```

2. Using AOF (Append-Only File):
   ```bash
   # Ensure AOF is enabled in redis.conf
   # appendonly yes
   
   # Copy the appendonly.aof file from the container
   docker cp advanced-search-engine_redis_1:/data/appendonly.aof ./backups/appendonly.aof
   ```

### Restoring Redis data

1. Stop the Redis container:
   ```bash
   docker-compose stop redis
   ```

2. Copy backup file to the container:
   ```bash
   # For RDB backup
   docker cp ./backups/dump.rdb advanced-search-engine_redis_1:/data/dump.rdb
   
   # For AOF backup
   docker cp ./backups/appendonly.aof advanced-search-engine_redis_1:/data/appendonly.aof
   ```

3. Start the Redis container:
   ```bash
   docker-compose start redis
   ```

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**
   - Check if Redis is running: `docker-compose ps redis`
   - Verify Redis port is accessible: `telnet localhost 6379`
   - Check Redis logs: `docker-compose logs redis`

2. **API Not Responding**
   - Check API logs: `docker-compose logs rest-api`
   - Verify API container is running: `docker-compose ps rest-api`
   - Check Nginx configuration: `docker-compose logs nginx`

3. **Search Functionality Issues**
   - Verify Python search engine is running: `docker-compose logs search-engine`
   - Check API to Python communication
   - Test direct access to Python server: `curl http://search-engine:8000/health`

### Health Checks

To perform a health check on all components:

```bash
# Quick system check
docker-compose ps

# Check individual component health
curl http://localhost/api/admin/health

# Get search engine statistics
curl http://localhost/api/admin/stats
```

For detailed logs:

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs rest-api
docker-compose logs search-engine
docker-compose logs redis
```

### Performance Tuning

1. **Redis Performance**
   - Adjust Redis memory settings in docker-compose.yml
   - Configure Redis eviction policies for better cache management
   - Consider Redis cluster for high availability and performance

2. **Search Engine Performance**
   - Adjust cache TTL settings based on your data volatility
   - Optimize indexing parameters in the engine configuration
   - Consider sharding the index for very large document collections

3. **REST API Performance**
   - Increase Node.js memory limits for high traffic scenarios
   - Implement horizontal scaling with multiple API instances
   - Adjust connection pool sizes for database connections

4. **Nginx Performance**
   - Enable gzip compression
   - Implement proper caching headers
   - Tune worker processes and connections
   - Consider using a CDN for static content

## Scaling Strategies

### Vertical Scaling

For moderate workloads, vertical scaling can be effective:

1. Increase resources for existing containers:
   ```yaml
   services:
     rest-api:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

2. Use larger Redis instance with more memory

### Horizontal Scaling

For high traffic workloads, consider horizontal scaling:

1. Implement multiple REST API instances:
   ```yaml
   services:
     rest-api:
       deploy:
         replicas: 3
   ```

2. Set up Redis Cluster for distributed caching

3. Implement load balancing with Nginx:
   ```nginx
   upstream api_servers {
       server rest-api-1:3000;
       server rest-api-2:3000;
       server rest-api-3:3000;
   }
   
   server {
       listen 80;
       
       location /api/ {
           proxy_pass http://api_servers;
       }
   }
   ```

4. Consider using Kubernetes for orchestration:
   - Use StatefulSets for Redis
   - Use Deployments for the REST API
   - Use Services for networking
   - Use Ingress for HTTP routing

## Security Recommendations

1. **Authentication & Authorization**
   - Implement JWT-based authentication for the API
   - Add role-based access control (RBAC)
   - Secure admin endpoints

2. **Network Security**
   - Use HTTPS with strong SSL/TLS settings
   - Implement rate limiting
   - Set up a Web Application Firewall (WAF)

3. **Docker Security**
   - Use non-root users in containers
   - Scan images for vulnerabilities
   - Implement least privilege principles

4. **Environment Security**
   - Use environment variables for secrets
   - Consider using a secret management solution like HashiCorp Vault
   - Restrict access to production environments

## Continuous Integration & Deployment

### CI/CD Pipeline

1. Set up a CI/CD pipeline with GitHub Actions or Jenkins:
   - Run tests on pull requests
   - Build Docker images
   - Push to a container registry
   - Deploy to staging/production

2. Create a sample GitHub Actions workflow:
   ```yaml
   name: CI/CD Pipeline
   
   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.9
         - name: Install dependencies
           run: pip install -r requirements.txt
         - name: Run tests
           run: pytest
     
     build:
       needs: test
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Build and push Docker images
           uses: docker/build-push-action@v2
           with:
             context: .
             push: true
             tags: username/search-engine:latest
     
     deploy:
       needs: build
       runs-on: ubuntu-latest
       steps:
         - name: Deploy to production
           run: |
             # Deploy commands here
   ```

### Deployment Strategies

1. **Blue-Green Deployment**
   - Maintain two identical production environments
   - Route traffic to one environment while updating the other

2. **Canary Releases**
   - Gradually roll out changes to a small subset of users
   - Monitor for issues before full deployment

3. **Rolling Updates**
   - Update instances one by one to avoid downtime

## Maintenance Procedures

### Regular Maintenance Tasks

1. **Database Maintenance**
   - Run periodic Redis BGSAVE operations
   - Monitor memory usage
   - Implement automatic backup schedules

2. **Log Rotation**
   - Configure log rotation to prevent disk space issues
   - Archive old logs for compliance

3. **Security Updates**
   - Regularly update base Docker images
   - Apply security patches
   - Run vulnerability scans

### Monitoring Alerts

Set up alerts for:
- High CPU/Memory usage
- Slow response times
- Error rate increases
- Cache hit ratio drops
- Disk space warnings
- Security incidents

## Disaster Recovery

1. **Backup Strategy**
   - Frequent backups of Redis data
   - Store backups in multiple locations
   - Test restore procedures regularly

2. **Recovery Plan**
   - Document step-by-step recovery procedures
   - Assign roles and responsibilities
   - Conduct recovery drills

3. **High Availability Setup**
   - Implement Redis replication
   - Use multiple application instances
   - Set up failover mechanisms