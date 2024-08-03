import requests
from bs4 import BeautifulSoup
import redis
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class AdvancedSearchEngine:
    def __init__(self, urls):
        self.urls = urls
        self.index = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.create_index()

    def create_index(self):
        for url in self.urls:
            content = self.fetch_content(url)
            self.documents.append(content)
            self.index_content(url, content)
        self.create_tfidf_index()

    def fetch_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()

    def index_content(self, url, content):
        self.index.set(url, content)

    def create_tfidf_index(self):
        tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        self.tfidf_matrix = tfidf_matrix.toarray()
        self.features = self.vectorizer.get_feature_names_out()

    def search(self, query):
        query_vec = self.vectorizer.transform([query]).toarray()[0]
        similarities = np.dot(self.tfidf_matrix, query_vec)
        sorted_similarities = np.argsort(similarities)[::-1]
        results = [(self.urls[i], similarities[i]) for i in sorted_similarities if similarities[i] > 0]
        return results

if __name__ == "__main__":
    urls = [
        "https://www.msn.com/en-in/sports/olympics?ocid=msedgntp",
        "https://www.msn.com/en-in/feed?ocid=msedgntp",
        "https://www.njit.edu/bursar/important-dates"
    ]
    search_engine = AdvancedSearchEngine(urls)
    query = input("Enter a search query: ")
    results = search_engine.search(query)
    if results:
        print(f"Search results for '{query}':")
        for result in results:
            print(result)
    else:
        print(f"No results found for '{query}'")
