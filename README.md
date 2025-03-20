# Advanced Search Engine

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
├── search_engine/             # Python search engine core
│   ├── __init__.py
│   ├── document.py            # Document representation
│   ├── indexer.py             # Document indexing logic
│   ├── engine.py              # Main search engine orchestration
│   ├── rankers/               # Ranking strategies
│   │   ├── __init__.py
│   │   └── tfidf_ranker.py    # TF-IDF based ranker
│   └── factories/             # Factory implementations
│       └── ranker_factory.py  # Factory for creating rankers
├── rest_api/                  # Node.js REST API (future)
├── tests/                     # Tests
│   └── python/                # Python tests
│       ├── test_document.py
│       ├── test_indexer.py
│       ├── test_tfidf_ranker.py
│       ├── test_ranker_factory.py
│       └── test_engine.py
├── .gitignore                 # Git ignore file
├── setup.py                   # Package setup script
└── README.md                  # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher (for future REST API)
- Redis (for future caching implementation)

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

### Running Tests

Run the tests using pytest:

```bash
pytest
```

For test coverage report:

```bash
pytest --cov=search_engine tests/
```

For lint checks:

```bash
pylint search_engine tests
```

## Usage

### Basic Example

```python
from search_engine.engine import SearchEngine

# Initialize the search engine
engine = SearchEngine()

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

## Development Roadmap

- [x] Phase 1: Core Python search engine with TF-IDF ranking
- [ ] Phase 2: Redis caching integration
- [ ] Phase 3: Node.js REST API development
- [ ] Phase 4: Deployment and optimization

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