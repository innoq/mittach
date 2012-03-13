import os

os.environ["MITTACH_CONFIG_MODE"] = "testing" # XXX: hard-codes statusq.NAME
from mittach import app, database


class Test(object):

    def setup_method(self, method):
        # reset database
        self.db = database.connect(app.config)
        self.db.flushall()

    def test_creation(self):
        data = { "title": "FooBar", "date": 20120310, "slots": 3 }

        assert database.create_event(self.db, data) == True
