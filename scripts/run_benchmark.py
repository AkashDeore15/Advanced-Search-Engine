#!/usr/bin/env python
"""
Benchmark script for the Advanced Search Engine.
This script indexes a large number of test documents and performs
search queries to measure performance with and without caching.
"""
import os
import time
import requests
import argparse
import json
import random
import statistics
from concurrent.futures import ThreadPoolExecutor

# API endpoint
API_BASE_URL = "http://localhost:3000/api"

# Sample topics for generating test data
TOPICS = [
    "artificial intelligence", "machine learning", "natural language processing",
    "deep learning", "neural networks", "computer vision", "robotics",
    "data science", "big data", "cloud computing", "internet of things",
    "cybersecurity", "blockchain", "quantum computing", "augmented reality",
    "virtual reality", "web development", "mobile development", "devops",
    "software engineering"
]

# Sample content templates
CONTENT_TEMPLATES = [
    "This document discusses {adj} approaches to {topic} and related technologies.",
    "An overview of {adj} {topic} techniques and applications.",
    "Understanding {topic}: {adj} methods and implementations.",
    "{adj} {topic} fundamentals and best practices.",
    "The future of {topic}: {adj} trends and predictions.",
    "How {adj} {topic} is changing the technology landscape.",
    "{topic} in practice: {adj} case studies and examples.",
    "Building {adj} systems with {topic} technologies.",
    "{adj} {topic}: challenges and opportunities.",
    "Exploring {adj} frameworks for {topic} applications."
]

# Sample adjectives
ADJECTIVES = [
    "advanced", "modern", "innovative", "cutting-edge", "revolutionary",
    "state-of-the-art", "emerging", "new", "latest", "next-generation",
    "fundamental", "essential", "comprehensive", "practical", "theoretical",
    "introductory", "intermediate", "advanced", "expert-level", "specialized"
]


def generate_test_document(doc_id):
    """Generate a test document with random content."""
    topic = random.choice(TOPICS)
    adj = random.choice(ADJECTIVES)
    template = random.choice(CONTENT_TEMPLATES)
    
    content = template.format(topic=topic, adj=adj)
    
    # Add some random additional content
    additional_sentences = random.randint(3, 10)
    for _ in range(additional_sentences):
        subtopic = random.choice(TOPICS)
        content += f" {random.choice(CONTENT_TEMPLATES).format(topic=subtopic, adj=random.choice(ADJECTIVES)).lower()}"
    
    return {
        'doc_id': f"doc_{doc_id}",
        'content': content,
        'metadata': {
            'topic': topic,
            'length': len(content),
            'generated': True
        }
    }


def generate_test_query():
    """Generate a test search query."""
    topic = random.choice(TOPICS)
    query_templates = [
        "{topic}",
        "advanced {topic}",
        "{topic} applications",
        "{topic} techniques",
        "{topic} best practices",
        "modern {topic}",
        "{topic} frameworks",
        "{topic} examples"
    ]
    return random.choice(query_templates).format(topic=topic)


def index_documents(num_documents, batch_size=100):
    """Index a number of test documents in batches."""
    print(f"Indexing {num_documents} test documents (batch size: {batch_size})...")
    
    start_time = time.time()
    indexed_count = 0
    
    for i in range(0, num_documents, batch_size):
        batch_end = min(i + batch_size, num_documents)
        documents = [generate_test_document(j) for j in range(i, batch_end)]
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/documents/batch",
                json={"documents": documents}
            )
            
            if response.status_code == 200:
                result = response.json()
                indexed_count += result.get('indexed_count', 0)
                print(f"Indexed {indexed_count}/{num_documents} documents...", end="\r")
            else:
                print(f"Error indexing batch {i}-{batch_end}: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Exception indexing batch {i}-{batch_end}: {e}")
    
    duration = time.time() - start_time
    docs_per_second = indexed_count / duration if duration > 0 else 0
    
    print(f"\nIndexed {indexed_count} documents in {duration:.2f} seconds ({docs_per_second:.2f} docs/sec)")
    return indexed_count


def perform_search(query, use_cache=True):
    """Perform a search query and return the results and time taken."""
    headers = {}
    if not use_cache:
        headers['Cache-Control'] = 'no-cache'
    
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/search",
            params={"q": query},
            headers=headers
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                'query': query,
                'count': result.get('count', 0),
                'duration': duration,
                'success': True
            }
        else:
            return {
                'query': query,
                'error': f"{response.status_code} {response.text}",
                'duration': duration,
                'success': False
            }
    except Exception as e:
        duration = time.time() - start_time
        return {
            'query': query,
            'error': str(e),
            'duration': duration,
            'success': False
        }


def benchmark_search(num_queries=100, iterations=3, use_threads=True):
    """Benchmark search performance with and without cache."""
    print(f"Generating {num_queries} test queries...")
    queries = [generate_test_query() for _ in range(num_queries)]
    
    # Clear cache before starting
    try:
        requests.post(f"{API_BASE_URL}/admin/cache/clear")
    except Exception as e:
        print(f"Warning: Failed to clear cache: {e}")
    
    # First pass: No cache
    print("\nBenchmarking search WITHOUT cache...")
    no_cache_results = []
    
    if use_threads:
        # Use thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=10) as executor:
            # For each query, run multiple iterations
            for query in queries:
                for _ in range(iterations):
                    future = executor.submit(perform_search, query, False)
                    no_cache_results.append(future.result())
                    print(f"Completed {len(no_cache_results)}/{num_queries * iterations} searches without cache...", end="\r")
    else:
        # Sequential execution
        for i, query in enumerate(queries):
            for j in range(iterations):
                result = perform_search(query, False)
                no_cache_results.append(result)
                print(f"Completed {i * iterations + j + 1}/{num_queries * iterations} searches without cache...", end="\r")
    
    # Calculate statistics
    no_cache_times = [r['duration'] for r in no_cache_results if r['success']]
    no_cache_avg = statistics.mean(no_cache_times) if no_cache_times else 0
    no_cache_median = statistics.median(no_cache_times) if no_cache_times else 0
    
    print(f"\nSearch WITHOUT cache: Avg {no_cache_avg:.6f}s, Median {no_cache_median:.6f}s")
    
    # Second pass: With cache
    print("\nBenchmarking search WITH cache...")
    cache_results = []
    
    # Warm up cache with one pass
    print("Warming up cache...")
    for query in queries:
        perform_search(query, True)
    
    # Benchmark with cache
    if use_threads:
        # Use thread pool for parallel execution
        with ThreadPoolExecutor(max_workers=10) as executor:
            # For each query, run multiple iterations
            for query in queries:
                for _ in range(iterations):
                    future = executor.submit(perform_search, query, True)
                    cache_results.append(future.result())
                    print(f"Completed {len(cache_results)}/{num_queries * iterations} searches with cache...", end="\r")
    else:
        # Sequential execution
        for i, query in enumerate(queries):
            for j in range(iterations):
                result = perform_search(query, True)
                cache_results.append(result)
                print(f"Completed {i * iterations + j + 1}/{num_queries * iterations} searches with cache...", end="\r")
    
    # Calculate statistics
    cache_times = [r['duration'] for r in cache_results if r['success']]
    cache_avg = statistics.mean(cache_times) if cache_times else 0
    cache_median = statistics.median(cache_times) if cache_times else 0
    
    print(f"\nSearch WITH cache: Avg {cache_avg:.6f}s, Median {cache_median:.6f}s")
    
    # Calculate improvement
    if no_cache_avg > 0:
        improvement = ((no_cache_avg - cache_avg) / no_cache_avg) * 100
        print(f"\nPerformance improvement: {improvement:.2f}%")
    
    return {
        'no_cache': {
            'avg_time': no_cache_avg,
            'median_time': no_cache_median,
            'num_queries': len(no_cache_times)
        },
        'with_cache': {
            'avg_time': cache_avg,
            'median_time': cache_median,
            'num_queries': len(cache_times)
        },
        'improvement_percent': improvement if no_cache_avg > 0 else 0
    }


def get_engine_stats():
    """Get search engine statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/stats")
        if response.status_code == 200:
            return response.json().get('stats', {})
        else:
            print(f"Error getting stats: {response.status_code} {response.text}")
            return {}
    except Exception as e:
        print(f"Exception getting stats: {e}")
        return {}


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Search Engine Benchmark Tool')
    parser.add_argument('--documents', type=int, default=1000, help='Number of documents to index')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for indexing')
    parser.add_argument('--queries', type=int, default=50, help='Number of test queries to generate')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations per query')
    parser.add_argument('--no-threading', action='store_true', help='Disable threading for search benchmark')
    parser.add_argument('--skip-indexing', action='store_true', help='Skip document indexing phase')
    parser.add_argument('--output', type=str, help='Save results to JSON file')
    
    args = parser.parse_args()
    
    results = {
        'timestamp': time.time(),
        'setup': vars(args)
    }
    
    # Index documents
    if not args.skip_indexing:
        indexed_count = index_documents(args.documents, args.batch_size)
        results['indexing'] = {
            'documents_indexed': indexed_count,
            'documents_requested': args.documents
        }
    
    # Get initial stats
    initial_stats = get_engine_stats()
    results['initial_stats'] = initial_stats
    
    # Benchmark search
    search_results = benchmark_search(args.queries, args.iterations, not args.no_threading)
    results['search'] = search_results
    
    # Get final stats
    final_stats = get_engine_stats()
    results['final_stats'] = final_stats
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    if 'indexing' in results:
        print(f"\nDocuments indexed: {results['indexing']['documents_indexed']}")
    
    print(f"\nSearch queries: {args.queries} (x{args.iterations} iterations)")
    print(f"\nWithout cache:")
    print(f"  Average query time: {search_results['no_cache']['avg_time']:.6f} seconds")
    print(f"  Median query time: {search_results['no_cache']['median_time']:.6f} seconds")
    
    print(f"\nWith cache:")
    print(f"  Average query time: {search_results['with_cache']['avg_time']:.6f} seconds")
    print(f"  Median query time: {search_results['with_cache']['median_time']:.6f} seconds")
    
    print(f"\nPerformance improvement: {search_results['improvement_percent']:.2f}%")
    
    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()