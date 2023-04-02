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
import sys
import logging

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from config import DB_PATH, PORT, DEBUG
from indexer import AptIndexer
from conn import DbSession
from models import Package

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AptSearch")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    db = DbSession()
    packages = db.session.query(Package).filter(Package.name.like('%' + query + '%')).all()
    db.session.close()
    return render_template('search.html', packages=packages)

@app.route('/package/<name>')
def package(name):
    db = DbSession()
    package = db.session.query(Package).filter_by(name=name).first()
    depends = []
    recommends = []
    suggests = []
    conflicts = []
    replaces = []
    provides = []

    if package.depends:
        depends = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.depends.split(', ')]
    if package.recommends:
        recommends = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.recommends.split(', ')]
    if package.suggests:
        suggests = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.suggests.split(', ')]
    if package.conflicts:
        conflicts = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.conflicts.split(', ')]
    if package.replaces:
        replaces = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.replaces.split(', ')]
    if package.provides:
        provides = [db.session.query(Package).filter(Package.name.like(dep.split(' ')[0])).first() for dep in package.provides.split(', ')]

    db.session.close()
    return render_template(
        'package.html', 
        package=package, 
        depends=depends, 
        recommends=recommends, 
        suggests=suggests, 
        conflicts=conflicts, 
        replaces=replaces, 
        provides=provides
    )

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'index':
            AptIndexer().index()
        elif sys.argv[1] == 'serve':
            app.run(debug=DEBUG, port=PORT)
            sys.exit(0)
            
    print('Usage: python main.py [index|serve]')
