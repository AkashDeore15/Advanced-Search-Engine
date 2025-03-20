"""
Ranker Factory module for the Advanced Search Engine.
Implements the Factory Method pattern for creating different ranking strategy objects.
"""
from ..rankers.tfidf_ranker import TfIdfRanker

class RankerFactory:
    """
    Factory for creating ranker objects.
    Implements the Factory Method pattern to produce different ranking strategies.
    """

    @staticmethod
    def create_ranker(ranker_type, **kwargs):
        """
        Create a ranker of the specified type.

        Args:
            ranker_type (str): The type of ranker to create (e.g., 'tfidf', 'bm25').
            **kwargs: Additional arguments to pass to the ranker constructor.

        Returns:
            Ranker: An instance of the requested ranker type.

        Raises:
            ValueError: If the ranker type is not supported.
        """
        ranker_type = ranker_type.lower()
        if ranker_type == 'tfidf':
            return TfIdfRanker(**kwargs)
        # Future expansion:
        # elif ranker_type == 'bm25':
        #     return Bm25Ranker(**kwargs)
        # If not a supported ranker type
        raise ValueError(f"Unsupported ranker type: {ranker_type}")

    @staticmethod
    def get_available_rankers():
        """
        Get a list of available ranker types.

        Returns:
            list: List of available ranker type names.
        """
        return ['tfidf']  # Add more as they are implemented
