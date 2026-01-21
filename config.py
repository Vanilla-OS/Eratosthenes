import os

DB_PATH = "eratosthenes.db"
BRANCHES = {
    "main": "https://repo3.vanillaos.org/20251129T023004Z/dists/sid/@/@/Packages",
    "testing": "https://repo3.vanillaos.org/20260116T142445Z/dists/sid/@/@/Packages",
}
ARCHS = ["amd64", "arm64", "i386"]
REPO_COMPONENTS = ["main", "contrib", "non-free-firmware", "non-free"]
PORT = 6001
DEBUG = True