from __future__ import absolute_import, division, with_statement

import os

from flask import Flask, g, request, url_for, redirect, abort, \
    render_template, flash, render_template_string

from . import database


__version__ = "0.1.0"

NAME = "Mittach" # XXX: unnecessary?
MODE = os.environ.get("%s_CONFIG_MODE" % NAME.upper(), "development").lower() # TODO: document


class RemoteUserMiddleware(object):
    """
    WSGI middleware to inject a REMOTE_USER for debugging purposes
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        from getpass import getuser
        environ["REMOTE_USER"] = getuser()
        return self.app(environ, start_response)


# initialize application
app = Flask(__name__)
app.config.from_object("%s.config.%sConfig" % (__name__, MODE.capitalize()))
if app.debug:
    app.wsgi_app = RemoteUserMiddleware(app.wsgi_app)
# TODO: support for custom settings (via `from_envvar / `from_pyfile`) - NB: must be mode-dependent
with app.open_resource("../secret") as fd: # XXX: potential security hazard as the same secret is used for production and development/testing
    app.config["SECRET_KEY"] = fd.read()


@app.before_request
def before_request():
    g.current_user = request.environ.get("REMOTE_USER")
    if not g.current_user:
        abort(403)
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
    errors = validate(event)
    if (len(errors) == 0):
        database.create_event(g.db, event)
        flash("Happening erstellt.", "success")
        return redirect(url_for("list_events"))
    else:
        for field, msg in errors.items():
            flash(msg, "error")
        return render_template_string('{% extends "layout.html" %} {% block body %} {% include "create_event.html" %} {% endblock %}', new_event=event)


def validate(event):
    errors = {}
    try:
        int(event["slots"])
    except ValueError:
        errors["slots"] = "Slots muss eine Zahl sein."

    try:
        int(event["date"])
    except ValueError:
        errors["date"] = "Ungueltiges Datum."

    if (event["title"] is None or event["title"].strip() == ""):
        errors["title"] = "Titel fehlt."

    return errors


@app.route("/events/<event_id>/my_booking", methods=["POST"])
def handle_booking(event_id):
    if request.form.get("_method", "PUT").upper() == "DELETE":
        return cancel_event(event_id)
    else:
        return book_event(event_id)


@app.route("/events/<event_id>/my_booking", methods=["PUT"])
def book_event(event_id):
    if database.book_event(g.db, event_id, g.current_user):
        flash("Anmeldung erfolgreich.", "success")
    else:
        flash("Anmeldung nicht erfolgreich.", "error")
    return redirect(url_for("list_events"))


@app.route("/events/<event_id>/my_booking", methods=["DELETE"])
def cancel_event(event_id):
    if database.cancel_event(g.db, event_id, g.current_user):
        flash("Abmeldung erfolgreich.", "success")
    else:
        flash("Abmeldung nicht erfolgreich.", "error")
    return redirect(url_for("list_events"))
