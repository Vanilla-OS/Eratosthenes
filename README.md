<div align="center">
<img src="assets/dark.png?raw=true#gh-dark-mode-only" height="40">
<img src="assets/light.png?raw=true#gh-light-mode-only" height="40">
</div>

---
<p align="center">Eratosthenes is an APT repository browser and indexer, designed for Vanilla OS.</p>

## Requirements
You can install all the requirements with `pip install -r requirements.txt`.

## Configuration
To configure your repository and database, edit the `config.py` file:
```python
DB_PATH = 'eratosthenes.db'
REPO_URL = 'https://your.repo/Packages'
PORT = 5000
DEBUG = True
```

## Usage
To run the indexer, simply run `python eratosthenes.py index`. This will create
the database and index the repository.

To run the web server, run `python eratosthenes.py serve`. This will start a web
server on port `5000` by default, but you can change it in the configuration
file as explained above.

## Development

### Environment

```bash
python3 -m venv env
poenv install
```

### Start the server

```bash
python eratosthenes.py serve
```

### Re-build Tailwind CSS

```bash
pnpx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch
```

## Why Eratosthenes?
Eratosthenes was a Greek mathematician, astronomer, and geographer. This is a
repository indexer and browser, so I thought it was a good name.
