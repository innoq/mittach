import os

os.environ["MITTACH_CONFIG_MODE"] = "testing"
from mittach.web import app, database


class Test(object):

    def setup_method(self, method):
        assert app.config["MODE"] == "testing"
        # reset database
        self.db = database.connect(app.config)
        self.db.flushall()

    def test_creation(self):
        data = { "title": "FooBar", "details": "", "date": 20120310,
                "slots": 3, "vegetarian": True }

        assert database.create_event(self.db, data) == 1

    def test_event_list(self):
        defaults = { "details": "", "date": 0, "vegetarian": False }
        for i, data in enumerate([{ "title": "Foo", "slots": 1 },
                { "title": "Bar", "slots": 2, "vegetarian": True },
                { "title": "Baz", "slots": 3 }]):
            _data = {}
            _data.update(defaults)
            _data.update(data)
            database.create_event(self.db, _data)

        events = database.list_events(self.db)
        assert len(events) == 3
        assert ["Baz", "Bar", "Foo"] == [event["title"] for event in events]
