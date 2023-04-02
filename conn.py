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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError

from config import DB_PATH


Model = declarative_base()

class DbSession:
    def __init__(self):
        self.engine = create_engine('sqlite:///' + DB_PATH, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
