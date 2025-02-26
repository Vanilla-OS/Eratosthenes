<div align="center">
<img src="assets/dark.png?raw=true#gh-dark-mode-only" height="40">
<img src="assets/light.png?raw=true#gh-light-mode-only" height="40">
</div>

---
<p align="center">Eratosthenes is an APT repository browser and indexer, designed for Vanilla OS.</p>

## Requirements

You can install all the requirements with `pip install -r requirements.txt`.

## Usage

To run the indexer, simply run `python eratosthenes.py index`. This will create
the database and index the repository.

To run the web server, run `python eratosthenes.py serve`. This will start a web
server on port `5000` by default, but you can change it in the configuration
file as explained below.

## Configuration

To configure your repository and database, add a `config.py` file:

```py
import os

DB_PATH = "eratosthenes.db"
BRANCHES = {
    "main": "https://repo2.vanillaos.org/dists/sid/@/binary-amd64/Packages",
    "testing": "https://testing.vanillaos.org/dists/sid/@/binary-amd64/Packages",
}
REPO_COMPONENTS = ["main", "contrib", "non-free-firmware", "non-free"]
PORT = 6001
DEBUG = True
```

Where,

- `DB_PATH` allows setting the path to the Eratosthenes database containing the repository index.
- `BRANCHES` allows adding branches from multiple repositories or within the same repository (it is displayed in the frontend in the same order as configured here).
- `REPO_COMPONENTS` allows adding components or tags for repositories.
- `PORT` allows setting Eratosthenes to run in a custom port.
- `DEBUG` allows displaying a debug log in the server's output

## Setting up a Development server

### Set the Environment

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

## Why the name Eratosthenes?

Eratosthenes was a Greek mathematician, astronomer, and geographer. This is a
repository indexer and browser, so I thought it was a good name.
