# encoding: utf-8

from __future__ import absolute_import, division, with_statement

import os

from datetime import date, datetime, timedelta
from collections import defaultdict

from flask import Flask, g, request, url_for, make_response, redirect, abort, \
    render_template, flash, render_template_string

from .config import read_config
from . import database


NAME = "Mittach" # XXX: unnecessary?


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


# initialize application -- TODO: move into function in order to pass parameters like config location
app = Flask(__package__, instance_relative_config=True)
config = {
    "mode": os.environ.get("MITTACH_CONFIG_MODE"), # XXX: hack for testing; this should not be necessary
    "secret": None
}
if not config["mode"]:
    try:
        config = read_config(app.open_instance_resource("config.ini"))
    except IOError: # XXX: temporary workaround until `__init__.py` is nothing but metadata
        import sys
        print >> sys.stderr, "[WARNING] bootstrapping configuration"
        config["mode"] = "development"
app.config.from_object("%s.config.%sConfig" % (__package__, config["mode"].capitalize()))
app.config["MODE"] = config["mode"]
app.config["SECRET_KEY"] = config["secret"]
if app.debug:
    app.wsgi_app = RemoteUserMiddleware(app.wsgi_app)


@app.before_request
def before_request():
    g.current_user = request.environ.get("REMOTE_USER")
    if not g.current_user:
        abort(403)
    g.db = database.connect(app.config)

    last_month_end = date.today().replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    g.last_month = {
        "start": str(last_month_start),
        "end": str(last_month_end),
    }
    g.last_month["name"] = month_name(g.last_month["start"], True)


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
        "date": request.form["date"].replace("-", ""), # TODO: use `normalize_date`
        "title": request.form["title"],
        "details": request.form["details"],
        "slots": request.form["slots"]
    }
    errors = validate(event)
    if (len(errors) == 0):
        database.create_event(g.db, event)
        flash("Termin erstellt.", "success")
        return redirect(url_for("list_events"))
    else:
        for field, msg in errors.items():
            flash(msg, "error")
        return render_template_string('{% extends "layout.html" %} {% block body %} {% include "create_event.html" %} {% endblock %}', new_event=event)


@app.route("/reports/<start>/<end>")
def report_bookings(start, end):
    """
    displays a simple report of events plus bookings in the given time frame

    both start and end date are ISO-8601 date strings
    """
    try:
        start, end = map(normalize_date, (start, end))
    except ValueError:
        abort(400)

    events_by_user = defaultdict(lambda: [])
    for event in database.list_events(g.db, start, end):
        for username in event["bookings"]: # TODO: limit by AuthZ / user
            date = format_date(event["date"], True)
            events_by_user[username].append(date)

    rows = ["Mitarbeiter; Anzahl; Details"]
    rows += [";".join([username, unicode(len(dates)), ", ".join(dates)])
            for username, dates in events_by_user.items()]

    response = make_response("\n".join(rows))
    response.headers["Content-Type"] = "text/plain"
    response.headers["Content-Disposition"] = "attachment;filename=%s_%s.csv" % (
            start, end)
    return response


def validate(event):
    errors = {}

    try:
        int(event["slots"])
    except ValueError:
        event["slots"] = -1 # XXX: hacky?

    date = event["date"]
    try:
        assert len(date) == 8
        int(date)
    except (AssertionError, ValueError):
        errors["date"] = u"Ungültiges Datum."

    if (event["title"] is None or event["title"].strip() == ""):
        errors["title"] = "Speisentitel fehlt."

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


def format_date(value, include_weekday=False): # XXX: does not belong here
    """
    converts an ISO-8601-like integer into a date string:
    20120315 -> "2012-03-15 (Donnerstag)"
    """
    date = str(value)
    date = "%s-%s-%s" % (date[0:4], date[4:6], date[6:8])

    if include_weekday:
        weekday = datetime.strptime(date, "%Y-%m-%d").weekday()
        weekday = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                "Samstag", "Sonntag")[weekday]
        date += " (%s)" % weekday

    return date


def month_name(date, include_year=False):
    """
    returns the (German) name of the month based on a ISO-8601 date string
    "2012-03-15" -> "März 2012"
    """
    # XXX: partially duplicates `normalize_date`
    try:
        assert len(date) == 10
        assert date[4] == date[7] == "-"
    except (AssertionError, ValueError):
        raise ValueError("invalid date format")

    month = int(date[5:7]) - 1 # TODO: use `datetime` for this
    res = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
            "August", "September", "Oktober", "November", "Dezember"][month]

    if include_year:
        res += " %s" % date[0:4] # TODO: use `datetime` for this

    return res


def normalize_date(value): # XXX: does not belong here
    """
    converts an ISO-8601 date string into an integer:
    "2012-03-15" -> 20120315

    raises ValueError if date format is not ISO-8601
    """
    try:
        assert len(value) == 10
        assert value[4] == value[7] == "-"
        date = int(value.replace("-", ""))
    except (AssertionError, ValueError):
        raise ValueError("invalid date format")
    return date

app.jinja_env.filters["format_date"] = format_date # XXX: does not belong here!
