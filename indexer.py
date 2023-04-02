# Eratostene - an APT repository browser and indexer, designed for Vanilla OS.
# Copyright (C) 2023 Vanilla OS <https://vanillaos.org>

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
import sqlite3
import logging
import sqlite3
import requests
from config import DB_PATH, REPO_URL

logger = logging.getLogger("AptIndexer")

class AptIndexer:
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.cursor = self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS packages
            (id INTEGER PRIMARY KEY, name TEXT, version TEXT, description TEXT, section TEXT, homepage TEXT, maintainer TEXT, depends TEXT, recommends TEXT, suggests TEXT, conflicts TEXT, replaces TEXT, provides TEXT, filename TEXT)''')
        self.db.commit()

    def index(self):
        logger.info("Indexing packages...")
        self.cursor.execute('DELETE FROM packages')
        self.db.commit()
        packages = requests.get(REPO_URL).text.split('\n\n')
        values = []

        for package in packages:
            if package == '':
                continue

            package = package.split('\n')

            if len(package) < 6:
                continue

            logger.info("Indexing package: %s", package[0].split(': ')[1])

            name = package[0].split(': ')[1]
            version = package[1].split(': ')[1]
            description = package[2].split(': ')[1]
            section = package[3].split(': ')[1]
            homepage = package[4].split(': ')[1]
            maintainer = package[5].split(': ')[1]
            depends = package[6].split(': ')[1]
            recommends = package[7].split(': ')[1]
            suggests = package[8].split(': ')[1]
            conflicts = package[9].split(': ')[1]
            replaces = package[10].split(': ')[1]
            provides = package[11].split(': ')[1]
            filename = package[12].split(': ')[1]
            values.append((
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
                filename
            ))
        
        self.cursor.executemany('INSERT INTO packages (name, version, description, section, homepage, maintainer, depends, recommends, suggests, conflicts, replaces, provides, filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
        self.db.commit()
        
        logger.info("Indexing finished.")
