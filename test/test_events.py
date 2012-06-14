import os

os.environ["MITTACH_CONFIG_MODE"] = "testing" # FIXME: obsolete
from mittach.web import app, database


class Test(object):

    def setup_method(self, method):
        # reset database
        self.db = database.connect(app.config)
        self.db.flushall()

    def test_creation(self):
        data = { "title": "FooBar", "details": "", "date": 20120310, "slots": 3 }

        assert database.create_event(self.db, data) == 1

    def test_event_list(self):
        data = { "title": "Foo", "details": "", "date": 0, "slots": 1 }
        database.create_event(self.db, data)
        data = { "title": "Bar", "details": "", "date": 0, "slots": 2 }
        database.create_event(self.db, data)
        data = { "title": "Baz", "details": "", "date": 0, "slots": 3 }
        database.create_event(self.db, data)

        events = database.list_events(self.db)
        assert len(events) == 3
        assert ["Baz", "Bar", "Foo"] == [event["title"] for event in events]
