#!/usr/bin/env python
"""
Bridge script for interfacing between Node.js and the Python search engine.
This script accepts commands and parameters as arguments, executes them
on the search engine, and returns the results as JSON.
"""
import sys
import os
import json
import traceback

# Add the search engine path to sys.path
search_engine_path = os.environ.get('SEARCH_ENGINE_PATH', '../search_engine')
sys.path.append(os.path.abspath(search_engine_path))

# Import the search engine
try:
    from search_engine.engine import SearchEngine
except ImportError:
    print(json.dumps({
        'error': 'Failed to import search_engine module',
        'details': traceback.format_exc()
    }))
    sys.exit(1)

def init_search_engine():
    """Initialize the search engine with Redis caching."""
    redis_host = os.environ.get('REDIS_HOST', '172.31.80.1')
    redis_port = int(os.environ.get('REDIS_PORT', 6379))
    redis_db = int(os.environ.get('REDIS_DB', 0))
    
    try:
        engine = SearchEngine(
            enable_cache=True,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_db=redis_db
        )
        return engine
    except Exception as e:
        # Fall back to non-cached search engine
        print(json.dumps({
            'warning': 'Failed to initialize caching, falling back to non-cached engine',
            'details': str(e)
        }), file=sys.stderr)
        return SearchEngine(enable_cache=False)

def execute_command(command, params):
    """Execute a command on the search engine."""
    engine = init_search_engine()
    
    if command == 'search':
        query = params.get('query', '')
        top_n = params.get('top_n', 10)
        results = engine.search(query, top_n)
        return {'results': results}
    
    elif command == 'index_document':
        doc_id = params.get('doc_id', '')
        content = params.get('content', '')
        metadata = params.get('metadata', {})
        success = engine.index_document(doc_id, content, metadata)
        return {'success': success}
    
    elif command == 'index_documents':
        documents = params.get('documents', [])
        count = engine.index_documents(documents)
        return {'indexed_count': count}
    
    elif command == 'remove_document':
        doc_id = params.get('doc_id', '')
        success = engine.remove_document(doc_id)
        return {'success': success}
    
    elif command == 'get_document':
        doc_id = params.get('doc_id', '')
        doc = engine.get_document(doc_id)
        if doc:
            return {
                'doc_id': doc.doc_id,
                'content': doc.content,
                'metadata': doc.metadata
            }
        return {'error': 'Document not found'}
    
    elif command == 'get_stats':
        stats = engine.get_stats()
        return {'stats': stats}
    
    elif command == 'clear_cache':
        if engine.enable_cache and engine.cache_manager:
            success = engine.clear_cache()
            return {'success': success}
        return {'success': False, 'reason': 'Cache not enabled'}
    
    else:
        return {'error': f'Unknown command: {command}'}

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Command argument is required'}))
        sys.exit(1)
    
    command = sys.argv[1]
    params = {}
    
    if len(sys.argv) > 2:
        try:
            params = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print(json.dumps({'error': 'Invalid JSON parameters'}))
            sys.exit(1)
    
    try:
        result = execute_command(command, params)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({
            'error': 'Command execution failed',
            'details': str(e),
            'traceback': traceback.format_exc()
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()