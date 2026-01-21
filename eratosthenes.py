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

import logging
import sys

from flask import Flask, render_template, request, abort

from config import DEBUG, PORT, REPO_COMPONENTS, ARCHS
from conn import DbSession
from indexer import AptIndexer
from models import Package

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AptSearch")

app = Flask(__name__)


@app.route("/")
def index():
    branch = request.cookies.get("branch", "main")
    arch = request.cookies.get("arch", "amd64")
    return render_template("index.html", branch=branch, current_arch=arch, archs=ARCHS)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/search")
def search():
    query = request.args.get("q")
    branch = request.args.get("branch") or request.cookies.get("branch", "main")
    arch = request.args.get("arch") or request.cookies.get("arch", "amd64")

    if not query:
        return abort(404)

    db = DbSession()
    packages = (
        db.session.query(Package)
        .filter(Package.name.like(f"%{query}%"))
        .filter(Package.branch == branch, Package.arch == arch)
        .all()
    )
    db.session.close()
    return render_template(
        "search.html",
        packages=packages,
        show_search_bar=True,
        query=query,
        branch=branch,
        current_arch=arch,
        archs=ARCHS,
    )


@app.route("/api/pkg/<name>")
@app.route("/package/<name>")
def package(name):
    branch = request.cookies.get("branch", "main")
    arch = request.args.get("arch") or request.cookies.get("arch", "amd64")
    db = DbSession()
    package = db.session.query(Package).filter_by(name=name, branch=branch, arch=arch).first()
    depends = []
    recommends = []
    suggests = []
    conflicts = []
    replaces = []
    provides = []

    if not package:
        if "/api/" in request.url_rule.rule:
            return {"error": "Package not found"}, 404
        return render_template("404.html"), 404

    if package.depends:
        depends = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.depends.split(", ")
        ]
    if package.recommends:
        recommends = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.recommends.split(", ")
        ]
    if package.suggests:
        suggests = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.suggests.split(", ")
        ]
    if package.conflicts:
        conflicts = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.conflicts.split(", ")
        ]
    if package.replaces:
        replaces = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.replaces.split(", ")
        ]
    if package.provides:
        provides = [
            db.session.query(Package)
            .filter(Package.name.like(dep.split(" ")[0]))
            .first()
            for dep in package.provides.split(", ")
        ]

    db.session.close()

    if "/api/" in request.url_rule.rule:
        package_info = {
            "name": package.name,
            "description": package.description,
            "version": package.version,
            "arch": package.arch,
            "depends": [dep.name for dep in depends if hasattr(dep, "name")],
            "recommends": [rec.name for rec in recommends if hasattr(rec, "name")],
            "suggests": [sug.name for sug in suggests if hasattr(sug, "name")],
            "conflicts": [conf.name for conf in conflicts if hasattr(conf, "name")],
            "replaces": [rep.name for rep in replaces if hasattr(rep, "name")],
            "provides": [prov.name for prov in provides if hasattr(prov, "name")],
        }
        return package_info, 200

    return render_template(
        "package.html",
        package=package,
        depends=depends,
        recommends=recommends,
        suggests=suggests,
        conflicts=conflicts,
        replaces=replaces,
        provides=provides,
        show_search_bar=True,
        branch=branch,
        current_arch=arch,
        archs=ARCHS,
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "index":
            apt = AptIndexer()
            apt.cleanup()
            apt.index()
        elif sys.argv[1] == "serve":
            app.run(debug=DEBUG, port=PORT)
            sys.exit(0)

    print("Usage: python main.py [index|serve]")
