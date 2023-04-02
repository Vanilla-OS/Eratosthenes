# Eratosthenes - an APT repository browser and indexer, designed for Vanilla OS.
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
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from conn import Model, DbSession

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        try:
            db = SqlSession()
            db.session.add(obj)
            db.session.commit()
            db.close()
            logging.info("New data: %s" % type(obj).__name__)
            return obj
        except exc.IntegrityError:
            logging.error("IntegrityError for data: %s" % type(obj).__name__)
            return False

class Package(Model, BaseMixin):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    version = Column(String(80), unique=False, nullable=False)
    description = Column(String(512), unique=False, nullable=False)
    section = Column(String(80), unique=False, nullable=False)
    homepage = Column(String(512), unique=False, nullable=False)
    maintainer = Column(String(512), unique=False, nullable=False)
    depends = Column(String(512), unique=False, nullable=False)
    recommends = Column(String(512), unique=False, nullable=False)
    suggests = Column(String(512), unique=False, nullable=False)
    conflicts = Column(String(512), unique=False, nullable=False)
    replaces = Column(String(512), unique=False, nullable=False)
    provides = Column(String(512), unique=False, nullable=False)
    filename = Column(String(512), unique=False, nullable=False)

    def __repr__(self):
        return '<Package %r>' % self.name