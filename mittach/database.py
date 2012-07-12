from redis import StrictRedis


def debug():
    raise StandardError("Don't panic! You're here by request of debug()")

def connect(config):
    cfg = config["DATABASE"]
    return StrictRedis(host=cfg["host"], port=cfg["port"], db=cfg["redis_db"])


def create_event(db, data):
    event_id = db.incr("events:enum")
    namespace = "events:%s" % event_id

    pipe = db.pipeline()
    pipe.lpush("events", event_id)
    pipe.set("%s:date" % namespace, data["date"])
    pipe.set("%s:title" % namespace, data["title"])
    pipe.set("%s:details" % namespace, data["details"])
    pipe.set("%s:slots" % namespace, data["slots"])
    if data["vegetarian"]:
        pipe.set("%s:vegetarian" % namespace, True)
    pipe.execute()

    return event_id

def get_count_events(db):
    return len(db.lrange("events", 0, -1))

def list_events(db, start=None, end=None):
    """
    returns a list of events, optionally limited to a time frame

    both start and end date are ISO-8601-like integers
    """
    scoped = start and end
    event_ids = db.lrange("events", 0, -1) # XXX: does not scale!?

    events = []
    for event_id in event_ids: # XXX: use `map`?
        namespace = "events:%s" % event_id
        date = format_date(db.get("%s:date" % namespace))
        if not scoped or start <= date <= end:
            slots = int(db.get("%s:slots" % namespace))
            event = {
                "id": int(event_id),
                "date": date,
                "title": db.get("%s:title" % namespace).decode("utf-8"),
                "details": (db.get("%s:details" % namespace) or "").decode("utf-8"),
                "slots": slots,
                "vegetarian": db.get("%s:vegetarian" % namespace) or False,
                "vegetarians": db.lrange("%s:vegetarians" % namespace, 0, -1),
                "bookings": db.lrange("%s:bookings" % namespace, 0, -1)
            }
            events.append(event)

    return events # TODO: use generator

def get_bookings(db,event_id):
    namespace = "events:%s" % event_id
    return db.lrange("%s:bookings" % namespace, 0, -1)

def book_event(db, event_id, username, vegetarian):
    namespace = "events:%s" % event_id

    slots = db.get("%s:slots" % namespace)

    pipe = db.pipeline()
    pipe.lrem("%s:bookings" % namespace, 0, username)
    pipe.rpush("%s:bookings" % namespace, username)
    if vegetarian:
        pipe.rpush("%s:vegetarians" % namespace, username)
    results = pipe.execute()

    if slots == -1 or results[1] <= slots:
        return True
    else:
        db.ltrim("%s:bookings" % namespace, 0, slots - 1)
        return False

def delete_event(db, event_id):
    namespace = "events:%s" % event_id
    try:
        pipe = db.pipeline()
        pipe.lrem("events", 1, event_id)
        pipe.lrem("%s:" % namespace, 1, "date")
        pipe.lrem("%s:" % namespace, 1, "title")
        pipe.lrem("%s:" % namespace, 1, "details")
        pipe.lrem("%s:" % namespace, 1, "slots")
        results = pipe.execute()
        erg = True
    except:
        erg = False



    return erg

def get_event(db, event_id):
    namespace = "events:%s" % event_id

    data = {
        "id": event_id,
        "date": db.get("%s:date" % namespace),
        "title": db.get("%s:title" % namespace),
        "details": db.get("%s:details" % namespace),
        "slots": db.get("%s:slots" % namespace),
        "vegetarian": db.get("%s:vegetarian" % namespace)
    }
    if data["vegetarian"] == None:
        data["vegetarian"] = False

    return data

def edit_event(db, event_id, data):
    namespace = "events:%s" % event_id

    pipe = db.pipeline()
    pipe.set("%s:date" % namespace, data["date"])
    pipe.set("%s:title" % namespace, data["title"])
    pipe.set("%s:details" % namespace, data["details"])
    pipe.set("%s:slots" % namespace, data["slots"])
    if data["vegetarian"]:
        pipe.set("%s:vegetarian" % namespace, True)
    pipe.execute()


def cancel_event(db, event_id, username):
    namespace = "events:%s" % event_id

    pipe = db.pipeline()
    pipe.lrem("%s:bookings" % namespace, 0, username)
    pipe.lrem("%s:vegetarians" % namespace, 0, username)
    results = pipe.execute()

    return results[0] > 0

def format_date(value, include_weekday=False): # XXX: does not belong here
    """
    if it's not already a date string, it converts an ISO-8601-like integer into a date string:
    20120315 -> "2012-03-15 (Donnerstag)"
    """

    date = value
    try:
        assert len(date) == 10
    except AssertionError:
        date = str(value)
        date = "%s-%s-%s" % (date[0:4], date[4:6], date[6:8])

    if include_weekday:
        weekday = datetime.strptime(date, "%Y-%m-%d").weekday()
        weekday = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                "Samstag", "Sonntag")[weekday]
        date += " (%s)" % weekday

    return date
