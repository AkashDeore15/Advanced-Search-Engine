"""
Server module for the Advanced Search Engine.
This provides a simple HTTP interface to the search engine for testing
and direct access if needed.
"""
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .engine import SearchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the search engine
engine = SearchEngine(
    enable_cache=True,
    redis_host=os.environ.get('REDIS_HOST', 'localhost'),
    redis_port=int(os.environ.get('REDIS_PORT', 6379)),
    redis_db=int(os.environ.get('REDIS_DB', 0))
)


class SearchEngineHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the search engine."""

    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _send_response(self, data, status_code=200):
        """Send JSON response."""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Health check endpoint
        if path == '/health':
            self._send_response({'status': 'ok'})
            return

        # Search endpoint
        if path == '/search':
            if 'q' not in query_params:
                self._send_response({'error': 'Query parameter q is required'}, 400)
                return

            query = query_params['q'][0]
            limit = int(query_params.get('limit', ['10'])[0])

            try:
                results = engine.search(query, limit)
                self._send_response({
                    'query': query,
                    'limit': limit,
                    'count': len(results),
                    'results': results
                })
            except Exception as e:
                logger.error(f"Search error: {e}")
                self._send_response({'error': str(e)}, 500)

            return

        # Get stats endpoint
        if path == '/stats':
            try:
                stats = engine.get_stats()
                self._send_response({'stats': stats})
            except Exception as e:
                logger.error(f"Stats error: {e}")
                self._send_response({'error': str(e)}, 500)
            return

        # If no matching endpoint, return 404
        self._send_response({'error': 'Not found'}, 404)

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_response({'error': 'Invalid JSON'}, 400)
            return

        # Index document endpoint
        if self.path == '/documents':
            if 'doc_id' not in data or 'content' not in data:
                self._send_response({'error': 'doc_id and content are required'}, 400)
                return

            try:
                result = engine.index_document(
                    data['doc_id'],
                    data['content'],
                    data.get('metadata', {})
                )
                self._send_response({'success': result, 'doc_id': data['doc_id']})
            except Exception as e:
                logger.error(f"Index document error: {e}")
                self._send_response({'error': str(e)}, 500)
            return

        # Index multiple documents endpoint
        if self.path == '/documents/batch':
            if 'documents' not in data or not isinstance(data['documents'], list):
                self._send_response({'error': 'documents array is required'}, 400)
                return

            try:
                count = engine.index_documents(data['documents'])
                self._send_response({
                    'indexed_count': count,
                    'total_count': len(data['documents'])
                })
            except Exception as e:
                logger.error(f"Index documents error: {e}")
                self._send_response({'error': str(e)}, 500)
            return

        # Clear cache endpoint
        if self.path == '/cache/clear':
            try:
                result = engine.clear_cache()
                self._send_response({'success': result})
            except Exception as e:
                logger.error(f"Clear cache error: {e}")
                self._send_response({'error': str(e)}, 500)
            return

        # If no matching endpoint, return 404
        self._send_response({'error': 'Not found'}, 404)

    def do_DELETE(self):
        """Handle DELETE requests."""
        # Extract document ID from path
        parts = self.path.split('/')
        if len(parts) >= 3 and parts[1] == 'documents':
            doc_id = parts[2]

            try:
                result = engine.remove_document(doc_id)
                self._send_response({'success': result, 'doc_id': doc_id})
            except Exception as e:
                logger.error(f"Remove document error: {e}")
                self._send_response({'error': str(e)}, 500)
            return

        # If no matching endpoint, return 404
        self._send_response({'error': 'Not found'}, 404)

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self._set_headers()


def run_server(host='0.0.0.0', port=8000):
    """Run the HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, SearchEngineHandler)
    logger.info(f'Starting server on http://{host}:{port}')
    httpd.serve_forever()


if __name__ == '__main__':
    # Get host and port from environment variables or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    run_server(host, port)
