import hashlib
import json
from datetime import datetime
import time

from reminders.exceptions import UnknownMethodException
from reminders.language import gs

class Reminder(object):
    _method = None
    _known_methods = ['reply', 'dm']
    
    timedelta = None
    error = None
    text = None

    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, value):
        if value not in self._known_methods:
            raise UnknownMethodException(value)
        
        self._method = value
        
    def __repr__(self):
        return '<Reminder text "%s", method "%s", error "%s" and timedelta "%s">' % (
            self.text, self.method, self.error, repr(self.timedelta))

    def serialize(self):
        return json.dumps({
            'text': self.text,
            'method': self._method
        })

    @classmethod
    def deserialize(cls, obj):
        result = cls()

        config = json.loads(obj)
        for item in config:
            setattr(result, item, config.get(item))

        return result

    def score(self):
        t = datetime.now() + self.timedelta
        return int(time.mktime(t.timetuple()))

    def execute(self, backend, extra):
        if not self.text: self.text = gs("REMINDER_PLACEHOLDER")
        text = {
            'reply': '@%s %s',
            'dm': 'd %s %s'
        }.get(self._method) % (extra['user'], self.text)
        backend.publish("reminders", text)

class Job(object):
    extra = dict()
    payload = None

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k, kw.get(k))

    def store(self, backend):
        h = hashlib.sha1()
        h.update(repr(self.extra) + repr(self.payload))
        k = "job.config.%s" % h.hexdigest()

        backend.hmset(k, {
            'extra': json.dumps(self.extra),
            'payload': self.payload.serialize()
        })

        backend.zadd("jobs", self.payload.score(), k)
    
    @classmethod
    def from_config_key(cls, backend, key):
        config = backend.hgetall(key)

        kw = {}
        for item in config:
            if item != 'payload':
                kw[item] = json.loads(config.get(item))
            else:
                kw[item] = Reminder.deserialize(config.get(item))
        
        backend.delete(key)
        return cls(**kw)  

    def execute(self, backend):
        self.payload.execute(backend, self.extra)
