# Advanced Search Engine

This project is an advanced search engine built using Python. It indexes the content of web pages and allows you to search for keywords across those pages using TF-IDF for finding important words and Redis for fast data retrieval. 

## Features

- **Content Fetching**: Retrieves content from specified URLs.
- **Indexing**: Stores the content of the pages using Redis for efficient retrieval.
- **Keyword Search**: Allows searching for keywords in the indexed content.
- **Ranking**: Utilizes TF-IDF to identify important words and rank search results accordingly.

## Technologies Used

- **Programming Language**: Python
- **Libraries**:
  - `requests`
  - `beautifulsoup4`
  - `redis`
  - `nltk`
- **Database**: Redis

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AkashDeore15/Search_Engine_Project.git
   cd Search_Engine_Project
   ```
2. **Install Dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Redis**:
   - **Install Redis**:
     - *Linux*:
       ```bash
       sudo apt-get install redis-server
       ```
     - *macOS* (using Homebrew):
       ```bash
       brew install redis
       ```
     - *Windows*: Download and install from the [official Redis website](https://redis.io/download).
   - **Start Redis Server**:
     ```bash
     redis-server
     ```

## Usage

1. **Index Web Pages**:
   - Specify the URLs to fetch and index in the `search_engine.py` script.
   - Run the script to fetch content and build the index:
     ```bash
     python search_engine.py --index
     ```
2. **Search for Keywords**:
   - After indexing, you can search for keywords:
     ```bash
     python search_engine.py --search "your search query"
     ```
   - The script will return ranked search results based on the TF-IDF scores.

## Project Structure

- `search_engine.py`: Main script for indexing and searching web page content.
- `requirements.txt`: List of required Python libraries.
- `README.md`: Project documentation.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository**.
2. **Create a New Branch**:
   ```bash
   git checkout -b feature-branch
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m 'Add new feature'
   ```
4. **Push to the Branch**:
   ```bash
   git push origin feature-branch
   ```
5. **Open a Pull Request**.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
