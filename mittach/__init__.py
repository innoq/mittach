from __future__ import absolute_import, division, with_statement

import os

from flask import Flask, g, request, url_for, redirect, render_template, \
    render_template_string

from . import database


__version__ = "0.1.0"

NAME = "Mittach" # XXX: unnecessary?
MODE = os.environ.get("%s_CONFIG_MODE" % NAME.upper(), "development").lower() # TODO: document


# initialize application
app = Flask(__name__)
app.config.from_object("%s.config.%sConfig" % (__name__, MODE.capitalize()))
# TODO: support for custom settings (via `from_envvar / `from_pyfile`) - NB: must be mode-dependent
with app.open_resource("../secret") as fd: # XXX: potential security hazard as the same secret is used for production and development/testing
    app.config["SECRET_KEY"] = fd.read()


@app.before_request
def before_request():
    g.current_user = "FND"
    g.db = database.connect(app.config)


@app.teardown_request
def teardown_request(exc):
    pass # no need to explicitly close the database connection


@app.route("/")
def root():
    return redirect(url_for("list_events"))


@app.route("/events")
def list_events():
    events = database.list_events(g.db)
    return render_template("index.html", events=events, new_event={})


@app.route("/events", methods=["POST"])
def create_event():
    event = {
        "date": request.form["date"],
        "title": request.form["title"],
        "slots": request.form["slots"]
    }
    database.create_event(g.db, event)
    return render_template_string('{% extends "layout.html" %} {% block body %} {% include "create_event.html" %} {% endblock %}', new_event=event)
