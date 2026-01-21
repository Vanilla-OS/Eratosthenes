# Eratosthenes - an APT repository browser and indexer, designed for Vanilla OS.
# Copyright (C) 2023-2025 Vanilla OS <https://vanillaos.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import lzma
import logging
import sqlite3
import requests
from io import BytesIO

from config import DB_PATH, BRANCHES, REPO_COMPONENTS, ARCHS

logger = logging.getLogger("AptIndexer")


class AptIndexer:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.cursor = self.db.cursor()
        self.create_schema()

    def create_schema(self):
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
                branch TEXT,
                arch TEXT
            )
        """
        )
        # Ensure 'arch' column exists in case an old table persists
        self.cursor.execute("PRAGMA table_info(packages)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if "arch" not in columns:
            self.cursor.execute("ALTER TABLE packages ADD COLUMN arch TEXT")
        self.db.commit()

    def cleanup(self):
        self.cursor.execute("DROP TABLE IF EXISTS packages")
        self.db.commit()
        self.create_schema()

    def index(self):
        for branch, base_url in BRANCHES.items():
            for component in REPO_COMPONENTS:
                for arch in ARCHS:
                    # Replace first @ with component and second @ with binary-<arch>
                    url = base_url.replace("@", component, 1).replace("@", f"binary-{arch}", 1)
                    
                    logger.info(
                        f"Indexing branch '{branch}' component '{component}' arch '{arch}' at {url}"
                    )
                    
                    response = None
                    # Try Packages, then Packages.gz, then Packages.xz
                    for ext in ["", ".gz", ".xz"]:
                        try:
                            fetch_url = url + ext
                            r = requests.get(fetch_url, timeout=10)
                            if r.status_code == 200:
                                if ext == ".gz":
                                    content = gzip.decompress(r.content).decode("utf-8")
                                elif ext == ".xz":
                                    content = lzma.decompress(r.content).decode("utf-8")
                                else:
                                    content = r.text
                                response = content
                                break
                        except Exception as e:
                            logger.error(f"Error fetching {fetch_url}: {e}")
                            continue
                    
                    if not response:
                        logger.warning(f"Could not find Packages for {branch}/{component}/{arch}")
                        continue

                    data = response.split("\n\n")
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
                                name = line.split(": ", 1)[1]
                            elif line.startswith("Version: "):
                                version = line.split(": ", 1)[1]
                            elif line.startswith("Description: "):
                                description = line.split(": ", 1)[1]
                            elif line.startswith("Section: "):
                                section = line.split(": ", 1)[1]
                            elif line.startswith("Homepage: "):
                                homepage = line.split(": ", 1)[1]
                            elif line.startswith("Maintainer: "):
                                maintainer = line.split(": ", 1)[1]
                            elif line.startswith("Depends: "):
                                depends = line.split(": ", 1)[1]
                            elif line.startswith("Recommends: "):
                                recommends = line.split(": ", 1)[1]
                            elif line.startswith("Suggests: "):
                                suggests = line.split(": ", 1)[1]
                            elif line.startswith("Conflicts: "):
                                conflicts = line.split(": ", 1)[1]
                            elif line.startswith("Replaces: "):
                                replaces = line.split(": ", 1)[1]
                            elif line.startswith("Provides: "):
                                provides = line.split(": ", 1)[1]
                            elif line.startswith("Filename: "):
                                filename = line.split(": ", 1)[1]

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
                                    arch,
                                )
                            )
                    
                    if values:
                        self.cursor.executemany(
                            """
                            INSERT INTO packages (
                                name, version, description, section, homepage, maintainer,
                                depends, recommends, suggests, conflicts, replaces, provides,
                                filename, branch, arch
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            values,
                        )
                        self.db.commit()
                        logger.info(
                            f"Finished indexing {len(values)} packages for branch '{branch}' component '{component}' arch '{arch}'."
                        )
