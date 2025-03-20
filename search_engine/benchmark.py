"""
Benchmark module for the Advanced Search Engine.
Provides utilities to measure search engine performance with and without caching.
"""
import time
import random
import statistics
import logging
from typing import Dict, List, Any
from .engine import SearchEngine

logger = logging.getLogger(__name__)


class SearchBenchmark:
    """
    Benchmarking utilities for measuring search engine performance.
    """

    def __init__(self, engine: SearchEngine):
        """
        Initialize a new SearchBenchmark instance.
        
        Args:
            engine (SearchEngine): The search engine to benchmark
        """
        self.engine = engine
        self.results = {}
    def generate_test_documents(self, count: int = 1000) -> List[Dict[str, Any]]:
        """
        Generate test documents for benchmarking.
        
        Args:
            count (int, optional): Number of documents to generate. Defaults to 1000.
        
        Returns:
            List[Dict[str, Any]]: List of generated documents
        """
        documents = []
        topics = [
            "artificial intelligence", "machine learning", "natural language processing",
            "deep learning", "neural networks", "computer vision", "robotics",
            "data science", "big data", "cloud computing", "internet of things",
            "cybersecurity", "blockchain", "quantum computing", "augmented reality",
            "virtual reality", "web development", "mobile development", "devops",
            "software engineering"
        ]
        adjectives = [
            "advanced", "modern", "innovative", "cutting-edge", "revolutionary",
            "state-of-the-art", "emerging", "new", "latest", "next-generation",
            "fundamental", "essential", "comprehensive", "practical", "theoretical",
            "introductory", "intermediate", "advanced", "expert-level", "specialized"
        ]
        content_templates = [
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
        for i in range(count):
            topic = random.choice(topics)
            adj = random.choice(adjectives)
            template = random.choice(content_templates)
            content = template.format(topic=topic, adj=adj)
            # Add some random additional content
            additional_sentences = random.randint(3, 10)
            for _ in range(additional_sentences):
                subtopic = random.choice(topics)
                content += f" {random.choice(content_templates).\
                               format(topic=subtopic, adj=random.choice(adjectives)).lower()}"
                documents.append({
                'doc_id': f"doc_{i+1}",
                'content': content,
                'metadata': {
                    'topic': topic,
                    'length': len(content),
                    'generated': True
                }
            })
        return documents

    def generate_test_queries(self, count: int = 100) -> List[str]:
        """
        Generate test queries for benchmarking.
        
        Args:
            count (int, optional): Number of queries to generate. Defaults to 100.
        
        Returns:
            List[str]: List of generated queries
        """
        topics = [
            "artificial intelligence", "machine learning", "neural networks",
            "deep learning", "data science", "cloud computing", "cybersecurity",
            "blockchain", "web development", "software engineering"
        ]
        query_templates = [
            "{topic}",
            "advanced {topic}",
            "{topic} applications",
            "{topic} techniques",
            "{topic} best practices",
            "modern {topic}",
            "{topic} frameworks",
            "{topic} examples",
            "{topic} challenges",
            "future of {topic}"
        ]
        queries = []
        for _ in range(count):
            topic = random.choice(topics)
            template = random.choice(query_templates)
            query = template.format(topic=topic)
            queries.append(query)
        return queries

    def run_indexing_benchmark(self, doc_count: int = 1000) -> Dict[str, Any]:
        """
        Benchmark document indexing performance.
        
        Args:
            doc_count (int, optional): Number of documents to index. Defaults to 1000.
        
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Generate test documents
        test_docs = self.generate_test_documents(doc_count)
        # Measure indexing time
        start_time = time.time()
        indexed_count = self.engine.index_documents(test_docs)
        end_time = time.time()
        duration = end_time - start_time
        docs_per_second = indexed_count / duration if duration > 0 else 0
        results = {
            'total_documents': doc_count,
            'indexed_documents': indexed_count,
            'total_duration_seconds': duration,
            'documents_per_second': docs_per_second
        }
        self.results['indexing'] = results
        return results

    def run_search_benchmark(self,\
                             query_count: int = 100,\
                                iterations: int = 3,\
                                    cache_enabled: bool = True) -> Dict[str, Any]:
        """
        Benchmark search performance with and without caching.
        
        Args:
            query_count (int, optional): Number of queries to run. Defaults to 100.
            iterations (int, optional): Number of iterations for each query. Defaults to 3.
            cache_enabled (bool, optional): Whether to enable caching. Defaults to True.
        
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Generate test queries
        test_queries = self.generate_test_queries(query_count)
        # First, run with cache disabled
        if self.engine.enable_cache:
            self.engine.disable_caching()
        # Measure search time without cache
        no_cache_times = []
        for query in test_queries:
            query_times = []
            for _ in range(iterations):
                start_time = time.time()
                self.engine.search(query)
                end_time = time.time()
                query_times.append(end_time - start_time)
            # Use the median time for this query
            no_cache_times.append(statistics.median(query_times))
        no_cache_avg = statistics.mean(no_cache_times)
        no_cache_median = statistics.median(no_cache_times)
        # Next, run with cache enabled (if requested)
        cache_avg = None
        cache_median = None
        cache_hit_ratio = None
        improvement_percent = None
        if cache_enabled:
            self.engine.enable_caching()
            self.engine.reset_cache_metrics()
            # Warm up the cache with one pass
            for query in test_queries:
                self.engine.search(query)
            # Measure search time with cache
            cache_times = []
            for query in test_queries:
                query_times = []
                for _ in range(iterations):
                    start_time = time.time()
                    self.engine.search(query)
                    end_time = time.time()
                    query_times.append(end_time - start_time)
                # Use the median time for this query
                cache_times.append(statistics.median(query_times))
            cache_avg = statistics.mean(cache_times)
            cache_median = statistics.median(cache_times)
            # Get cache hit ratio
            cache_metrics = self.engine.get_stats().get('cache', {})
            cache_hit_ratio = cache_metrics.get('hit_ratio', 0)
            # Calculate improvement
            improvement_percent = ((no_cache_avg - cache_avg) / no_cache_avg) * 100
        # Compile results
        results = {
            'queries_tested': query_count,
            'iterations_per_query': iterations,
            'no_cache': {
                'avg_time_seconds': no_cache_avg,
                'median_time_seconds': no_cache_median
            }
        }
        if cache_enabled:
            results['with_cache'] = {
                'avg_time_seconds': cache_avg,
                'median_time_seconds': cache_median,
                'hit_ratio': cache_hit_ratio
            }
            results['improvement_percent'] = improvement_percent
        self.results['search'] = results
        return results

    def run_full_benchmark(self,\
                           doc_count: int = 1000,\
                            query_count: int = 100,\
                                iterations: int = 3) -> Dict[str, Any]:
        """
        Run a complete benchmark suite including indexing and searching.
        
        Args:
            doc_count (int): Number of documents to index
            query_count (int): Number of queries to test
            iterations (int): Number of iterations per query
        
        Returns:
            Dict[str, Any]: Complete benchmark results
        """
        logger.info("Starting benchmark with %s documents and %s squeries", doc_count, query_count)
        # Run indexing benchmark
        indexing_results = self.run_indexing_benchmark(doc_count)
        logger.info("Indexed %s\
                     documents in %.2f seconds", indexing_results['indexed_documents'],\
                          indexing_results['total_duration_seconds'])
        # Run search benchmark
        search_results = self.run_search_benchmark(query_count, iterations, True)
        no_cache_avg = search_results['no_cache']['avg_time_seconds']
        cache_avg = search_results['with_cache']['avg_time_seconds']
        improvement = search_results['improvement_percent']
        logger.info("Search without cache: %.6f seconds (avg)", no_cache_avg)
        logger.info("Search with cache: %.6f seconds (avg)", cache_avg)
        logger.info("Improvement: %.2f%%", improvement)
        # Compile results
        results = {
            'indexing': indexing_results,
            'search': search_results,
            'timestamp': time.time()
        }
        self.results = results
        return results

    def print_summary(self) -> None:
        """Print a summary of the benchmark results."""
        if not self.results:
            print("No benchmark results available.")
            return
        print("\n" + "="*60)
        print("SEARCH ENGINE BENCHMARK RESULTS")
        print("="*60)
        if 'indexing' in self.results:
            idx = self.results['indexing']
            print("\nINDEXING PERFORMANCE:")
            print("Documents indexed: %s / %s",idx['indexed_documents'],\
                   idx['total_documents'])
            print("Total duration: %.2f seconds", idx['total_duration_seconds'])
            print("Documents per second: %.2f",idx['documents_per_second'])
        if 'search' in self.results:
            srch = self.results['search']
            print("\nSEARCH PERFORMANCE:")
            print("Queries tested: %s %s iterations)",srch['queries_tested'],\
                  srch['iterations_per_query'])
            print("\nWithout cache:")
            print("  Average query time: %s %.6f seconds", srch['no_cache'], ['avg_time_seconds'])
            print("  Median query time: %s %.6f seconds", srch['no_cache'], ['median_time_seconds'])
            if 'with_cache' in srch:
                print("\nWith cache:")
                print("  Average query time: %s %.6f seconds",srch['with_cache'],srch['with_cache'])
                print("  Median query time: %s %.6f seconds", srch['with_cache'],\
                      ['median_time_seconds'])
                print("  Cache hit ratio: %s %.2%}", srch['with_cache'],['hit_ratio'])
                print("\nPerformance improvement: %.2f%", srch['improvement_percent'])
        print("\n" + "="*60)
