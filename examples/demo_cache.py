"""
Demonstration of the search engine with Redis caching.
This script shows the performance improvement achieved by caching.
"""
import os
import sys
import logging
import time
# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from search_engine.engine import SearchEngine
from search_engine.benchmark import SearchBenchmark
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('demo_cache')


def main():
    """Run the demonstration."""
    print("\n" + "="*70)
    print("SEARCH ENGINE CACHING DEMONSTRATION")
    print("="*70)
    print("\nInitializing search engine with caching enabled...")
    engine = SearchEngine(enable_cache=True)
    # Check if Redis is available
    if not engine.enable_cache or not engine.cache_manager:
        print("\nERROR: Redis is not available. Please start Redis and try again.")
        print("Make sure Redis is running on localhost:6379 or update the connection parameters.")
        return
    # Create a benchmark instance
    benchmark = SearchBenchmark(engine)
    print("\nGenerating and indexing test documents...")
    num_docs = 1000
    docs = benchmark.generate_test_documents(num_docs)
    indexed_count = engine.index_documents(docs)
    print(f"Successfully indexed {indexed_count} documents.")
    # Test without cache
    print("\nRunning search without cache...")
    engine.disable_caching()
    query = "artificial intelligence applications"
    num_iterations = 5
    # First search to warm up
    engine.search(query) 
    # Measure time without cache
    no_cache_times = []
    for i in range(num_iterations):
        start_time = time.time()
        results = engine.search(query)
        end_time = time.time()
        no_cache_times.append(end_time - start_time)
        print(f"  Search {i+1}/{num_iterations}: {no_cache_times[-1]:.6f} seconds ({len(results)} results)") 
    avg_no_cache = sum(no_cache_times) / len(no_cache_times)
    print(f"\nAverage search time without cache: {avg_no_cache:.6f} seconds")
    # Test with cache
    print("\nRunning search with cache...")
    engine.enable_caching()
    engine.reset_cache_metrics() 
    # First search to populate cache
    print("  First search (populating cache)...")
    start_time = time.time()
    results = engine.search(query)
    end_time = time.time()
    print(f"  Cache population time: {end_time - start_time:.6f} seconds ({len(results)} results)") 
    # Measure time with cache
    cache_times = []
    for i in range(num_iterations):
        start_time = time.time()
        results = engine.search(query)
        end_time = time.time()
        cache_times.append(end_time - start_time)
        print(f"  Search {i+1}/{num_iterations}: {cache_times[-1]:.6f} seconds ({len(results)} results)")  
    avg_cache = sum(cache_times) / len(cache_times)
    print(f"\nAverage search time with cache: {avg_cache:.6f} seconds")
    # Calculate improvement
    improvement = ((avg_no_cache - avg_cache) / avg_no_cache) * 100
    print(f"\nPerformance improvement: {improvement:.2f}%")
    # Get cache metrics
    cache_stats = engine.get_performance_stats()['cache']
    print(f"\nCache hit ratio: {cache_stats['hit_ratio']:.2%}") 
    # Run full benchmark
    print("\n" + "="*70)
    print("RUNNING FULL BENCHMARK")
    print("="*70)
    print("\nThis will take a few minutes...\n") 
    benchmark.run_full_benchmark(
        doc_count=1000,
        query_count=50,
        iterations=3
    ) 
    benchmark.print_summary() 
    print("\nDemonstration complete.")

if __name__ == "__main__":
    main()
