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
    pipe.set("%s:slots" % namespace, data["slots"])
    pipe.execute()

    return event_id


def list_events(db):
    event_ids = db.lrange("events", 0, -1)

    events = []
    for event_id in event_ids: # XXX: use .map?
        namespace = "events:%s" % event_id
        event = {
            "id": int(event_id),
            "date": int(db.get("%s:date" % namespace)),
            "title": db.get("%s:title" % namespace),
            "slots": int(db.get("%s:slots" % namespace)),
            "bookings": []
        }
        events.append(event)

    return events
