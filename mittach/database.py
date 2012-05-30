from redis import StrictRedis


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
    pipe.execute()

    return event_id


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
        date = int(db.get("%s:date" % namespace))
        if not scoped or start <= date <= end:
            slots = int(db.get("%s:slots" % namespace))
            event = {
                "id": int(event_id),
                "date": date,
                "title": db.get("%s:title" % namespace).decode("utf-8"),
                "details": (db.get("%s:details" % namespace) or "").decode("utf-8"),
                "slots": slots,
                "bookings": db.lrange("%s:bookings" % namespace, 0, slots - 1)
            }
            events.append(event)

    return events # TODO: use generator


def book_event(db, event_id, username):
    namespace = "events:%s" % event_id

    slots = db.get("%s:slots" % namespace)

    pipe = db.pipeline()
    pipe.lrem("%s:bookings" % namespace, 0, username)
    pipe.rpush("%s:bookings" % namespace, username)
    index = pipe.execute()[-1]

    if index <= slots:
        return True
    else:
        db.ltrim("%s:bookings" % namespace, 0, slots - 1)
        return False


def cancel_event(db, event_id, username):
    namespace = "events:%s" % event_id
    return db.lrem("%s:bookings" % namespace, 0, username) > 0
