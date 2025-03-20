# Advanced Search Engine

A high-performance search engine using TF-IDF for document ranking, Redis caching for performance improvement, and a Node.js-powered REST API for data retrieval.

## Project Overview

This project aims to build a search engine with the following key features:

1. **TF-IDF Based Search Ranking** - Implements indexing and ranking of documents using TF-IDF to provide accurate and relevant results for user queries.
2. **Redis Caching** - Caches frequently accessed documents and/or query results to reduce response times by at least 40%.
3. **Node.js REST APIs** - Integrates Node.js for a fast, non-blocking REST API layer.
4. **OOP and Design Patterns** - Incorporates Factory Method, Command Pattern, LBYL, and EAFP principles.
5. **Team Knowledge-Sharing and Best Practices** - Sets up consistent documentation, code reviews, and knowledge-sharing sessions.
6. **Extensibility** - Lays the groundwork for future enhancements (e.g., advanced ranking algorithms such as BM25).# Advanced Search Engine

A high-performance search engine using TF-IDF for document ranking, Redis caching for performance improvement, and a Node.js-powered REST API for data retrieval.

## Project Overview

This project aims to build a search engine with the following key features:

1. **TF-IDF Based Search Ranking** - Implements indexing and ranking of documents using TF-IDF to provide accurate and relevant results for user queries.
2. **Redis Caching** - Caches frequently accessed documents and/or query results to reduce response times by at least 40%.
3. **Node.js REST APIs** - Integrates Node.js for a fast, non-blocking REST API layer.
4. **OOP and Design Patterns** - Incorporates Factory Method, Command Pattern, LBYL, and EAFP principles.
5. **Team Knowledge-Sharing and Best Practices** - Sets up consistent documentation, code reviews, and knowledge-sharing sessions.
6. **Extensibility** - Lays the groundwork for future enhancements (e.g., advanced ranking algorithms such as BM25).

## Project Structure

The project follows this structure:

```
Advanced-Search-Engine/
├── docs/                      # Documentation
│   └── cache.md               # Redis caching documentation
├── search_engine/             # Python search engine core
│   ├── __init__.py
│   ├── document.py            # Document representation
│   ├── indexer.py             # Document indexing logic
│   ├── engine.py              # Main search engine orchestration
│   ├── benchmark.py           # Performance benchmarking utilities
│   ├── cache/                 # Caching components
│   │   ├── __init__.py
│   │   ├── redis_client.py    # Redis client wrapper
│   │   └── cache_manager.py   # Cache management strategies
│   ├── rankers/               # Ranking strategies
│   │   ├── __init__.py
│   │   └── tfidf_ranker.py    # TF-IDF based ranker
│   └── factories/             # Factory implementations
│       └── ranker_factory.py  # Factory for creating rankers
├── rest_api/                  # Node.js REST API (future)
├── examples/                  # Example scripts
│   └── demo_cache.py          # Caching demonstration script
├── tests/                     # Tests
│   └── python/                # Python tests
│       ├── test_document.py
│       ├── test_indexer.py
│       ├── test_tfidf_ranker.py
│       ├── test_ranker_factory.py
│       ├── test_engine.py
│       ├── test_engine_cache.py
│       ├── test_redis_client.py
│       └── test_cache_manager.py
├── .gitignore                 # Git ignore file
├── setup.py                   # Package setup script
└── README.md                  # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Redis server (for caching)
- Node.js 16 or higher (for future REST API)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/advanced-search-engine.git
   cd advanced-search-engine
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install Redis (if not already installed):
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install redis-server
   
   # On macOS
   brew install redis
   
   # On Windows
   # Download from https://github.com/microsoftarchive/redis/releases
   ```

5. Start Redis server:
   ```bash
   # On Ubuntu/Debian
   sudo service redis-server start
   
   # On macOS
   brew services start redis
   
   # On Windows
   redis-server.exe
   ```

### Running Tests

Run the tests using pytest:

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/python/test_engine.py

# Run tests with cache (requires Redis)
pytest tests/python/test_engine_cache.py

# Skip tests that require Redis
pytest -k "not redis"

# Run tests with coverage report
pytest --cov=search_engine tests/
```

### Running the Demo

To run the caching demonstration:

```bash
# Ensure Redis is running
python examples/demo_cache.py
```

This demo will show the performance improvement achieved by Redis caching.

## Usage

### Basic Example

```python
from search_engine.engine import SearchEngine

# Initialize the search engine without caching
engine = SearchEngine(enable_cache=False)

# Index some documents
engine.index_document("doc1", "Python is a popular programming language.")
engine.index_document("doc2", "TF-IDF is used in search engines for ranking documents.")
engine.index_document("doc3", "Redis can be used as a cache to improve performance.")

# Search for documents
results = engine.search("programming language")

# Print the results
for result in results:
    print(f"Document ID: {result['doc_id']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
    print("---")
```

### With Redis Caching

```python
from search_engine.engine import SearchEngine

# Initialize the search engine with caching
engine = SearchEngine(
    enable_cache=True,
    redis_host='localhost',
    redis_port=6379,
    redis_db=0
)

# Index some documents
engine.index_document("doc1", "Python is a popular programming language.")
engine.index_document("doc2", "TF-IDF is used in search engines for ranking documents.")
engine.index_document("doc3", "Redis can be used as a cache to improve performance.")

# Search for documents (first search will be cached)
results = engine.search("programming language")

# Subsequent searches for the same query will be faster
results = engine.search("programming language")  # Retrieves from cache

# Get cache performance metrics
stats = engine.get_performance_stats()
print(f"Cache hit ratio: {stats['cache']['hit_ratio']:.2%}")

# Disable caching if needed
engine.disable_caching()

# Clear the cache
engine.clear_cache()

# Close the engine when done (closes Redis connections)
engine.close()
```

## Performance Benchmarking

The project includes a benchmarking utility to measure performance improvements:

```python
from search_engine.engine import SearchEngine
from search_engine.benchmark import SearchBenchmark

# Initialize the search engine
engine = SearchEngine(enable_cache=True)

# Create a benchmark instance
benchmark = SearchBenchmark(engine)

# Run the benchmark
results = benchmark.run_full_benchmark(
    doc_count=1000,  # Number of test documents
    query_count=100,  # Number of test queries
    iterations=3     # Iterations per query
)

# Print the results
benchmark.print_summary()
```

Typical performance improvements with Redis caching:
- Query performance: 40-90% faster with cached queries
- Document retrieval: Near-instant retrieval of cached documents
- Overall: Significant reduction in response times for repeated queries

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## Git Workflow

We use the following Git workflow:

1. **Feature Branches**: Create a new branch for each feature or bug fix
2. **Commit Messages**: Write clear, descriptive commit messages
3. **Pull Requests**: Submit a pull request for code review before merging
4. **Code Review**: At least one team member must review and approve changes
5. **Continuous Integration**: All tests must pass before merging

## License

This project is licensed under the MIT License - see the LICENSE file for details.