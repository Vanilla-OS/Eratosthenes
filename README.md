<div align="center">
<img src="internal/assets/static/images/dark.png?raw=true#gh-dark-mode-only" height="40">
<img src="internal/assets/static/images/light.png?raw=true#gh-light-mode-only" height="40">
</div>

---

<p align="center">Eratosthenes is an APT repository browser and indexer, designed for Vanilla OS.</p>

## Requirements

- Go 1.22 or later

## Installation

You can build Eratosthenes from source:

```bash
go build -o eratosthenes cmd/eratosthenes/main.go
```

## Usage

### Indexing

To index the repository, run:

```bash
./eratosthenes index
```

This will download the `Packages` files from the configured repositories and index them into a local Bitcask database (`eratosthenes_data` by default).

### Serving

To start the web server:

```bash
./eratosthenes serve --port 6001
```

The server will be available at `http://localhost:6001`.

## Configuration

Eratosthenes uses the Vanilla OS SDK configuration system. It supports cascading configuration from:
1. `/usr/share/eratosthenes/config.json`
2. `/etc/eratosthenes/config.json`
3. `$XDG_CONFIG_HOME/eratosthenes/config.json`
4. `./conf/eratosthenes/config.json`

Example `config.json`:

```json
{
    "port": 6001,
    "debug": true,
    "db_path": "eratosthenes_data",
    "branches": {
        "main": "https://repo3.vanillaos.org/20251129T023004Z/dists/sid/@/@/Packages",
        "testing": "https://repo3.vanillaos.org/20260116T142445Z/dists/sid/@/@/Packages"
    },
    "archs": ["amd64", "arm64"],
    "repo_components": ["main", "contrib", "non-free-firmware", "non-free"]
}
```

## Development

### Running Locally

```bash
go run cmd/eratosthenes/main.go serve
```

### Assets

Templates and static files are embedded in the binary. You can find them in `internal/assets`.

## Why the name Eratosthenes?

Eratosthenes was a Greek mathematician, astronomer, and geographer. This is a repository indexer and browser, so I thought it was a good name.
