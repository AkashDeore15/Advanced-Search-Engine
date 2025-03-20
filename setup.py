"""
Setup script for the Advanced Search Engine package.
"""
from setuptools import setup, find_packages

setup(
    name="advanced-search-engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "scikit-learn>=0.24.0",
        "scipy>=1.6.0",
        "redis>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pylint>=2.8.0",
        ],
    },
    python_requires=">=3.9",
    author="Akash Deore",
    author_email="akashdeore1999@gmail.com",
    description="A high-performance search engine using TF-IDF for document ranking",
    keywords="search, engine, tf-idf, redis, indexing",
    url="https://github.com/Akashdeore15/advanced-search-engine",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
)