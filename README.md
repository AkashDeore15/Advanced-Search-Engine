# Advanced Search Engine

A high-performance, **TF-IDF-based** search engine with **Redis** caching for optimized query performance. This project also exposes **Node.js REST APIs** for seamless data retrieval and integration. It demonstrates industry-standard design principles, **OOP**, and design patterns such as **Factory Method** and **Command Pattern**, as well as Python-specific best practices like **LBYL (Look Before You Leap)** and **EAFP (Easier to Ask for Forgiveness than Permission)**.

> **Key Highlights**  
> - **TF-IDF Ranking**: Provides relevance-based search results  
> - **Redis Caching**: Improves response time by caching frequently accessed data  
> - **Node.js REST API**: Offers a simple and scalable interface for querying documents  
> - **OOP & Design Patterns**: Factory Method, Command Pattern, SOLID principles  
> - **LBYL & EAFP**: Mix of defensive checks in Node.js and Python’s exception-based approach  

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Technologies & Dependencies](#technologies--dependencies)
6. [Installation & Setup](#installation--setup)
7. [Usage](#usage)
8. [Design Patterns & Principles](#design-patterns--principles)
9. [Testing](#testing)
10. [Performance Optimizations](#performance-optimizations)
11. [Contributing](#contributing)
12. [License](#license)
13. [Contact](#contact)

---

## Project Overview

The **Advanced Search Engine** is built with the goal of providing **fast** and **accurate** search results using **TF-IDF** for text ranking. A **Redis** cache layer helps boost performance by storing frequently accessed data or query results, leading to a reduction in response times (up to 40% improvement).

On top of the core search functionality, a **Node.js** REST API layer is included to integrate seamlessly with external clients or other microservices, improving the overall user experience and system maintainability.

By following best coding practices and design patterns, the project ensures cleaner code, easy maintenance, and straightforward scalability for future enhancements (e.g., adding **BM25**, **semantic search**, or advanced NLP pipelines).

---

## Features

1. **TF-IDF Ranking**  
   - Index documents based on their term frequencies.  
   - Rank search results using the TF-IDF scores for relevancy.

2. **Redis Caching**  
   - Cache frequently used data or query results in Redis.  
   - Configurable TTL to invalidate stale data.  
   - Achieves significant speed gains for repeated or popular queries.

3. **Node.js REST API**  
   - Expose endpoints for indexing, querying, and managing documents.  
   - Non-blocking I/O model for high throughput and reduced latency.  
   - Integrates with the Python engine using well-defined commands.

4. **OOP, LBYL, EAFP**  
   - Python modules leverage classes, encapsulation, and exception-based handling (EAFP).  
   - Node.js code demonstrates checking payload validity (LBYL) before processing.

5. **Design Patterns**  
   - **Factory Method**: Produces ranker objects (e.g., TF-IDF, BM25) from a single factory.  
   - **Command Pattern**: Encapsulates indexing, querying, and other actions into commands for easier maintainability and extensibility.

---

## Architecture

```
+------------------------+      +---------------------+
|     [Node.js]         |      |  [Python Engine]    |
|  REST API Layer       | ---> |  TF-IDF, Ranking    |
|  (Express / Fastify)  |      |  & Document Indexes |
+---------+-------------+      +----------+----------+
          |                             |
          v                             |
    +------------+                 +-----v-----+
    |   Redis    | <-------------- |  Caching  |
    +------------+                 +-----------+
```

1. **Node.js (REST API)**  
   - Receives client requests.  
   - Uses commands to index documents or retrieve query results.  
   - Validates input (LBYL).  
   - Communicates with Redis for cached responses.

2. **Python Engine (TF-IDF Core)**  
   - Maintains the document index.  
   - Calculates TF-IDF scores for queries.  
   - Uses EAFP by catching exceptions during indexing or searching.

3. **Redis**  
   - Serves as a high-speed caching mechanism.  
   - Stores query results or document data.

---

## Project Structure

A suggested directory layout for maintaining clear separation of concerns:

```
Advanced-Search-Engine/
├── docs/
│    ├── architecture.md          # Additional detailed docs
│    └── requirements.md          # Project requirements & user stories
├── search_engine/                # Python side (Core indexing & ranking logic)
│    ├── __init__.py
│    ├── engine.py                # Main orchestration for indexing & searching
│    ├── indexer.py               # Responsible for building the TF-IDF index
│    ├── rankers/
│    │    ├── __init__.py
│    │    ├── tfidf_ranker.py
│    │    └── bm25_ranker.py      # Example for future extension
│    └── factories/
│         └── ranker_factory.py   # Factory Method for rankers
├── rest_api/                     # Node.js side (REST API)
│    ├── package.json
│    ├── app.js                   # Entry point for Express or Fastify
│    ├── routes/
│    │    ├── searchRoutes.js     # GET /search
│    │    └── indexRoutes.js      # POST /documents
│    ├── controllers/
│    │    ├── searchController.js
│    │    └── indexController.js
│    ├── commands/
│    │    ├── indexDocumentCommand.js
│    │    └── queryCommand.js
│    └── utils/
│         └── redisClient.js      # Redis connection logic
├── tests/
│    ├── python/
│    │    ├── test_indexer.py
│    │    └── test_ranker.py
│    ├── node/
│    │    └── test_searchRoutes.js
│    │    └── test_indexRoutes.js
│    └── integration/
│         └── test_end_to_end.py
├── docker/
│    ├── Dockerfile.python
│    ├── Dockerfile.node
│    └── docker-compose.yml
├── .github/workflows/
│    └── ci-cd.yaml               # Optional GitHub Actions config
├── .env.example                  # Example environment variables
├── requirements.txt              # Python dependencies
└── README.md                     # This readme
```

---

## Technologies & Dependencies

1. **Python 3.9+**
   - Libraries: `numpy`, `scikit-learn` (for TF-IDF), `redis` (Python client)

2. **Node.js 16+ or 18+**
   - `Express` or `Fastify` for REST endpoints  
   - `redis` npm package for caching  
   - `mocha`, `chai`, or `jest` for tests

3. **Redis** (5.0+ recommended)

4. **Testing & QA**
   - **Pytest** (for Python)  
   - **Jest** / **Mocha** + **Chai** (for Node.js)  
   - Code linters: `flake8`, `pylint`, `eslint`

5. **Containerization & CI/CD** (optional)
   - **Docker**, **docker-compose**  
   - GitHub Actions / Jenkins

---

## Installation & Setup

Follow the instructions below to set up the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/AkashDeore15/Advanced-Search-Engine.git
cd Advanced-Search-Engine
```

### 2. Set Up Python Environment

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) If running a Python-based API (Flask/FastAPI), install relevant packages.

### 3. Set Up Node.js Environment

Inside the `rest_api/` directory:

```bash
cd rest_api
npm install
```

This will install packages defined in `package.json` (e.g., Express, Redis client).

### 4. Set Up Redis

You can install Redis locally or use Docker:

```bash
# Using Docker
docker run --name redis-server -p 6379:6379 -d redis
```

Ensure that your `.env` file or config points to the correct Redis host and port (e.g., `localhost:6379`).

---

## Usage

Below is a high-level example of how to **index** documents and **search** them.

1. **Start Redis** (if not already running)

```bash
docker start redis-server
```

2. **Run the Python Engine** (example)

```bash
# If you have a Python service for indexing
python search_engine/engine.py
```

3. **Start the Node.js REST API**

```bash
cd rest_api
npm start
```

4. **Index a Document** (cURL example)

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"title": "Sample Document", "content": "This is a test document for TF-IDF search."}' \
     http://localhost:3000/documents
```

5. **Search for Documents** (cURL example)

```bash
curl -X GET "http://localhost:3000/search?query=test"
```

> **Note**: The exact endpoints or ports may vary based on your configuration in `app.js` and environment variables.

---

## Design Patterns & Principles

1. **Factory Method**  
   - `ranker_factory.py` instantiates ranker objects like `TfIdfRanker` or a future `BM25Ranker`.

2. **Command Pattern**  
   - In Node.js, commands such as `indexDocumentCommand.js` or `queryCommand.js` encapsulate the logic to update or fetch documents.

3. **LBYL (Look Before You Leap)**  
   - In Node.js: Validate incoming JSON payloads, check required fields before processing to avoid runtime errors.

4. **EAFP (Easier to Ask for Forgiveness than Permission)**  
   - In Python: Try operations (e.g., dictionary lookups, file operations) and catch exceptions if something goes wrong.

5. **SOLID Principles**  
   - Classes have a single responsibility, are open for extension but closed for modification, and high-level modules depend on abstractions rather than concrete implementations.

---

## Testing

### Python Tests

Inside the project root:

```bash
pytest tests/python/
```

- **Unit Tests**: Verify the correctness of `indexer.py`, `tfidf_ranker.py`, etc.  
- **Integration Tests**: Test the overall search pipeline.

### Node.js Tests

Inside the `rest_api/` folder:

```bash
cd rest_api
npm test
```

- **Unit Tests**: For controllers, commands, and routes.  
- **Integration Tests**: Interact with the Python engine or a mock service to validate end-to-end flows.

---

## Performance Optimizations

- **Redis Caching**:  
  - Cache frequently accessed results to reduce computation.  
  - Use different Redis data structures (e.g., Hashes, Strings) as per use case.  
  - Configure an appropriate **TTL** (Time to Live).

- **Asynchronous I/O**:  
  - Node.js handles concurrent requests without blocking.  
  - Python can be wrapped in a lightweight service (Flask/FastAPI + gunicorn) with concurrency.

- **Scalability**:  
  - For large document sets, consider scaling out with additional search nodes or distributed indices.  
  - Shard or partition data across multiple instances if needed.

---

## Contributing

1. **Fork** the repository  
2. **Create** a new feature branch: `git checkout -b feature/some-improvement`  
3. **Commit** your changes: `git commit -m 'Add some improvement'`  
4. **Push** to the branch: `git push origin feature/some-improvement`  
5. **Create** a Pull Request on GitHub

Please ensure all **unit tests** and **integration tests** pass before submitting a PR. We also welcome suggestions to improve documentation, code quality, or add new features (e.g., advanced ranking algorithms, new caching strategies, etc.).

---

## License

This project is licensed under the [MIT License](LICENSE). Feel free to copy, modify, and distribute as per the license terms.

---

## Contact

For questions, suggestions, or issues, please open a GitHub [Issue](https://github.com/AkashDeore15/Advanced-Search-Engine/issues) or contact [@AkashDeore15](https://github.com/AkashDeore15).

---

**Happy Searching!**  
Thank you for using and contributing to the **Advanced Search Engine**. We hope this project helps you build and learn about high-performance search solutions, caching techniques, and best practices in modern software development.
