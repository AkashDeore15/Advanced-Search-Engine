"""
Engine module for the Advanced Search Engine.
Provides the main entry point for the search engine functionality.
"""
import time
import logging
import redis
from .document import Document
from .indexer import Indexer
from .factories.ranker_factory import RankerFactory
from .cache import CacheManager, RedisClient

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    The main search engine class that orchestrates indexing and searching.
    """

    def __init__(self, ranker_type='tfidf', enable_cache=True, *, \
                 redis_host='172.31.80.1', redis_port=6379, redis_db=0):
        """
        Initialize a new SearchEngine instance.

        Args:
            ranker_type (str, optional): The type of ranker to use. Defaults to 'tfidf'.
            enable_cache (bool, optional): Whether to enable caching. Defaults to True.
            redis_host (str, optional): Redis server hostname. Defaults to 'localhost'.
            redis_port (int, optional): Redis server port. Defaults to 6379.
            redis_db (int, optional): Redis database number. Defaults to 0.
        """
        self.indexer = Indexer()
        self.ranker_factory = RankerFactory()
        self.ranker = self.ranker_factory.create_ranker(ranker_type)
        # Set up caching
        self.enable_cache = enable_cache
        if enable_cache:
            try:
                redis_client = RedisClient(host=redis_host, port=redis_port, db=redis_db)
                self.cache_manager = CacheManager(redis_client=redis_client)
                logger.info("Cache enabled for search engine")
            except (redis.RedisError, ConnectionError, ValueError) as e:
                logger.warning("Failed to initialize cache: %s. Caching disabled.", e)
                self.enable_cache = False
                self.cache_manager = None
        else:
            self.cache_manager = None
            logger.info("Cache disabled for search engine")

    def index_document(self, doc_id, content, metadata=None):
        """
        Index a new document.

        Args:
            doc_id (str): Unique identifier for the document.
            content (str): The text content of the document.
            metadata (dict, optional): Additional metadata for the document. Defaults to None.

        Returns:
            bool: True if the document was indexed successfully.
        """
        start_time = time.time()
        doc = Document(doc_id, content, metadata)
        result = self.indexer.add_document(doc)
        # Update cache if successful
        if result and self.enable_cache and self.cache_manager:
            # Cache the document
            doc_data = doc.to_dict()
            self.cache_manager.cache_document(doc_id, doc_data)
            # Invalidate any cached queries that may be affected
            self.cache_manager.invalidate_all_queries()
            logger.debug("Document %s indexed and cached in %.3f seconds",doc_id,\
                          time.time() - start_time )
        else:
            logger.debug("Document %s indexed in %.3f seconds", doc_id, time.time() - start_time)
        return result

    def index_documents(self, documents_data):
        """
        Index multiple documents.

        Args:
            documents_data (list): List of dictionaries containing document data.
                Each dictionary should have 'doc_id' and 'content' keys,
                and an optional 'metadata' key.

        Returns:
            int: Number of documents successfully indexed.
        """
        start_time = time.time()
        documents = []
        for data in documents_data:
            try:
                doc = Document.from_dict(data)
                documents.append(doc)
            except ValueError:
                # Skip invalid documents
                continue
        # Add documents to the index
        count = self.indexer.add_documents(documents)
        # Update cache if successful
        if count > 0 and self.enable_cache and self.cache_manager:
            # Cache each document
            for doc in documents:
                self.cache_manager.cache_document(doc.doc_id, doc.to_dict())
            # Invalidate any cached queries that may be affected
            self.cache_manager.invalidate_all_queries()
            logger.debug(" %s documents indexed and cached in %.3f seconds", count,\
                          time.time() - start_time)
        else:
            logger.debug("%s documents indexed in %.3f seconds", count, time.time() - start_time)
        return count

    def remove_document(self, doc_id):
        """
        Remove a document from the index.

        Args:
            doc_id (str): The ID of the document to remove.

        Returns:
            bool: True if the document was removed successfully.
        """
        result = self.indexer.remove_document(doc_id)
        # Update cache if successful
        if result and self.enable_cache and self.cache_manager:
            # Remove from document cache
            self.cache_manager.invalidate_document(doc_id)
            # Invalidate any cached queries that may be affected
            self.cache_manager.invalidate_all_queries()
            logger.debug("Document %s removed and cache updated", doc_id)
        return result

    def get_document(self, doc_id):
        """
        Retrieve a document by its ID.

        Args:
            doc_id (str): The ID of the document to retrieve.

        Returns:
            Document: The requested document, or None if not found.
        """
        start_time = time.time()
        # Try to get from cache first
        if self.enable_cache and self.cache_manager:
            cached_doc = self.cache_manager.get_cached_document(doc_id)
            if cached_doc:
                # Reconstruct Document from cached data
                try:
                    doc = Document.from_dict(cached_doc)
                    logger.debug("Document %s retrieved from cache in\
                                  %.3f seconds", doc_id, time.time() - start_time)
                    return doc
                except ValueError as e:
                    logger.warning("Error reconstructing document from cache: %s", e)
        # Get from indexer if not in cache
        doc = self.indexer.get_document(doc_id)
        # Cache the document if found
        if doc and self.enable_cache and self.cache_manager:
            self.cache_manager.cache_document(doc_id, doc.to_dict())
        if doc:
            logger.debug("Document %s retrieved from index in\
                          %.3f seconds", doc_id, time.time() - start_time)
        else:
            logger.debug("Document %s not found (checked in\
                          %.3f seconds)", doc_id, time.time() - start_time)
        return doc
    def search(self, query, top_n=10):
        """
        Search for documents matching the query.

        Args:
            query (str): The search query.
            top_n (int, optional): The maximum number of results to return. Defaults to 10.

        Returns:
            list: List of dictionaries containing search results.
                Each dictionary has 'doc_id', 'content', 'metadata', and 'score' keys.
        """
        start_time = time.time()
        # Try to get from cache first
        if self.enable_cache and self.cache_manager:
            cached_results = self.cache_manager.get_cached_query_results(query, top_n)
            if cached_results:
                logger.debug("Query '%s' results retrieved from cache in\
                              %.3f seconds", query, time.time() - start_time)
                return cached_results
        # Build the index if it hasn't been built yet
        if not self.indexer.is_index_built:
            self.indexer.build_index()
        # Use the indexer to search for matching documents
        results = self.indexer.search(query, top_n)
        # Format the results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'doc_id': doc.doc_id,
                'content': doc.content,
                'metadata': doc.metadata,
                'score': float(score)
            })
        # Cache the results
        if self.enable_cache and self.cache_manager:
            self.cache_manager.cache_query_results(query, formatted_results, top_n)
            logger.debug("Query '%s' processed and cached in %.3f seconds", query,\
                          time.time() - start_time)
        else:
            logger.debug("Query '%s' processed in %.3f seconds", query, time.time() - start_time)
        return formatted_results

    def get_stats(self):
        """
        Get statistics about the search engine.

        Returns:
            dict: Dictionary containing search engine statistics.
        """
        start_time = time.time()
        # Try to get from cache first
        if self.enable_cache and self.cache_manager:
            cached_stats = self.cache_manager.get_cached_stats()
            if cached_stats:
                logger.debug("Stats retrieved from cache in %.3f seconds", time.time() - start_time)
                return cached_stats
        # Get stats from indexer
        stats = self.indexer.get_stats()
        stats['ranker_type'] = self.ranker.name
        # Add cache stats if available
        if self.enable_cache and self.cache_manager:
            cache_metrics = self.cache_manager.get_cache_metrics()
            stats['cache'] = cache_metrics
            # Cache the stats
            self.cache_manager.cache_stats(stats)
            logger.debug("Stats gathered and cached in %.3f seconds", time.time() - start_time)
        else:
            stats['cache_enabled'] = False
            logger.debug("Stats gathered in %.3f seconds", time.time() - start_time)
        return stats

    def change_ranker(self, ranker_type):
        """
        Change the ranker used by the search engine.

        Args:
            ranker_type (str): The type of ranker to use.

        Returns:
            bool: True if the ranker was changed successfully.
        """
        try:
            self.ranker = self.ranker_factory.create_ranker(ranker_type)
            # Invalidate cached queries if cache is enabled
            if self.enable_cache and self.cache_manager:
                self.cache_manager.invalidate_all_queries()
            return True
        except ValueError:
            return False
    def enable_caching(self):
        """
        Enable caching if it was disabled.
        
        Returns:
            bool: True if caching was enabled, False otherwise
        """
        if self.cache_manager:
            self.enable_cache = True
            self.cache_manager.enable_cache()
            logger.info("Caching enabled")
            return True
        logger.warning("Cannot enable caching: Cache manager not initialized")
        return False
    def disable_caching(self):
        """
        Disable caching.
        
        Returns:
            bool: True if caching was disabled
        """
        if self.cache_manager:
            self.enable_cache = False
            self.cache_manager.disable_cache()
            logger.info("Caching disabled")
        return True
    def clear_cache(self):
        """
        Clear all cached data.
        
        Returns:
            bool: True if cache was cleared, False otherwise
        """
        if self.enable_cache and self.cache_manager:
            result = self.cache_manager.invalidate_all()
            logger.info("Cache cleared")
            return result
        return False
    def reset_cache_metrics(self):
        """
        Reset cache performance metrics.
        
        Returns:
            bool: True if metrics were reset, False otherwise
        """
        if self.cache_manager:
            self.cache_manager.reset_metrics()
            logger.info("Cache metrics reset")
            return True
        return False
    def get_performance_stats(self):
        """
        Get detailed performance statistics.
        
        Returns:
            dict: Dictionary with performance metrics
        """
        stats = {
            'index_size': self.indexer.get_stats()
        }
        if self.enable_cache and self.cache_manager:
            stats['cache'] = self.cache_manager.get_cache_metrics()
        return stats
    def close(self):
        """
        Close the search engine and release resources.
        """
        if self.cache_manager:
            self.cache_manager.close()
            logger.info("Search engine resources released")
