# indexer.py
import logging
import sqlite3
import requests

from config import DB_PATH, BRANCHES, REPO_COMPONENTS

logger = logging.getLogger("AptIndexer")


class AptIndexer:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.cursor = self.db.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY,
                name TEXT,
                version TEXT,
                description TEXT,
                section TEXT,
                homepage TEXT,
                maintainer TEXT,
                depends TEXT,
                recommends TEXT,
                suggests TEXT,
                conflicts TEXT,
                replaces TEXT,
                provides TEXT,
                filename TEXT,
                branch TEXT
            )
        """
        )
        self.db.commit()

    def cleanup(self):
        self.cursor.execute("DELETE FROM packages")
        self.db.commit()

    def index(self):
        for branch, base_url in BRANCHES.items():
            for component in REPO_COMPONENTS:
                url = base_url.replace("@", component)
                logger.info(
                    f"Indexing branch '{branch}' component '{component}' at {url}"
                )
                data = requests.get(url).text.split("\n\n")
                values = []
                for pkg_raw in data:
                    if not pkg_raw.strip():
                        continue
                    lines = pkg_raw.split("\n")
                    name = version = description = section = homepage = maintainer = (
                        None
                    )
                    depends = recommends = suggests = conflicts = replaces = (
                        provides
                    ) = filename = None

                    for line in lines:
                        if line.startswith("Package: "):
                            name = line.split(": ")[1]
                        elif line.startswith("Version: "):
                            version = line.split(": ")[1]
                        elif line.startswith("Description: "):
                            description = line.split(": ")[1]
                        elif line.startswith("Section: "):
                            section = line.split(": ")[1]
                        elif line.startswith("Homepage: "):
                            homepage = line.split(": ")[1]
                        elif line.startswith("Maintainer: "):
                            maintainer = line.split(": ")[1]
                        elif line.startswith("Depends: "):
                            depends = line.split(": ")[1]
                        elif line.startswith("Recommends: "):
                            recommends = line.split(": ")[1]
                        elif line.startswith("Suggests: "):
                            suggests = line.split(": ")[1]
                        elif line.startswith("Conflicts: "):
                            conflicts = line.split(": ")[1]
                        elif line.startswith("Replaces: "):
                            replaces = line.split(": ")[1]
                        elif line.startswith("Provides: "):
                            provides = line.split(": ")[1]
                        elif line.startswith("Filename: "):
                            filename = line.split(": ")[1]

                    if name:
                        values.append(
                            (
                                name,
                                version,
                                description,
                                section,
                                homepage,
                                maintainer,
                                depends,
                                recommends,
                                suggests,
                                conflicts,
                                replaces,
                                provides,
                                filename,
                                branch,
                            )
                        )
                self.cursor.executemany(
                    """
                    INSERT INTO packages (
                        name, version, description, section, homepage, maintainer,
                        depends, recommends, suggests, conflicts, replaces, provides,
                        filename, branch
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    values,
                )
                self.db.commit()
                logger.info(
                    f"Finished indexing {len(values)} packages for branch '{branch}' component '{component}'."
                )
