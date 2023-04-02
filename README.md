# Eratostene
Eratostene is an APT repository browser and indexer, designed for Vanilla OS.

## Requirements
You can install all the requirements with `pip install -r requirements.txt`.

## Configuration
To configure your repository and database, edit the `config.py` file:
```python
DB_PATH = 'eratostene.db'
REPO_URL = 'https://your.repo/Packages'
PORT = 5000
DEBUG = True
```

## Usage
To run the indexer, simply run `python eratostene.py index`. This will create 
the database and index the repository.

To run the web server, run `python eratostene.py serve`. This will start a web 
server on port `5000` by default, but you can change it in the configuration
file as explained above.

## Why Eratostene?
Eratostene was a Greek mathematician, astronomer, and geographer. This is a
repository indexer and browser, so I thought it was a good name.
