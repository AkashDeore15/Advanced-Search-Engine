import requests
from bs4 import BeautifulSoup

class SimpleSearchEngine:
    def __init__(self, urls):
        self.urls = urls
        self.index = {}
        self.create_index()

    def create_index(self):
        for url in self.urls:
            content = self.fetch_content(url)
            self.index_content(url, content)

    def fetch_content(self, url):
        response = requests.get(url)
        return response.text

    def index_content(self, url, content):
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text().lower()
        words = text.split()
        for word in words:
            if word in self.index:
                self.index[word].add(url)
            else:
                self.index[word] = {url}

    def search(self, query):
        query = query.lower()
        results = self.index.get(query, set())
        return results

if __name__ == "__main__":
    urls = [
        "https://www.google.com",
        "https://mail.google.com",
        "https://www.njit.edu/bursar/important-dates"
    ]
    search_engine = SimpleSearchEngine(urls)
    query = input("Enter a search query: ")
    results = search_engine.search(query)
    if results:
        print(f"Search results for '{query}':")
        for result in results:
            print(result)
    else:
        print(f"No results found for '{query}'")
