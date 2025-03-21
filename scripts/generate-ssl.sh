#!/bin/bash
# Script to generate self-signed SSL certificates for development

# Create directories
mkdir -p nginx/ssl

# Generate private key
openssl genrsa -out nginx/ssl/server.key 2048

# Generate CSR (Certificate Signing Request)
openssl req -new -key nginx/ssl/server.key -out nginx/ssl/server.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in nginx/ssl/server.csr -signkey nginx/ssl/server.key -out nginx/ssl/server.crt

# Set permissions
chmod 600 nginx/ssl/server.key

echo "Self-signed SSL certificates generated successfully"
echo "Place them in the nginx/ssl directory"