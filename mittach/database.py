from redis import StrictRedis


def connect(config):
    cfg = config["DATABASE"]
    return StrictRedis(host=cfg["host"], port=cfg["port"], db=cfg["redis_db"])


def create_event(db, data):
    event_id = db.incr("events:enum")
    namespace = "events:%s" % event_id

    pipe = db.pipeline()
    pipe.sadd("events", event_id)
    pipe.set("%s:date" % namespace, data["date"])
    pipe.set("%s:title" % namespace, data["title"])
    pipe.set("%s:slots" % namespace, data["slots"])
    pipe.execute()

    return True
