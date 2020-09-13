import json
from abc import ABC, abstractmethod, abstractclassmethod


class Serializable(ABC):
    @abstractmethod
    def tojson(self):
        raise NotImplementedError("'tojson' method must be implemented.")

    def dump(self, fp, **kwds):
        obj = self.tojson()
        json.dump(obj, fp, **kwds)

    def dumps(self, **kwds):
        obj = self.tojson()
        return json.dumps(obj, **kwds)

    @abstractclassmethod
    def fromjson(cls, data):
        raise NotImplementedError("'fromjson' method must be implemented.")

    @classmethod
    def load(cls, fp, **kwds):
        obj = json.load(fp, **kwds)
        return cls.fromjson(obj)

    @classmethod
    def loads(cls, s, **kwds):
        obj = json.loads(s, **kwds)
        return cls.fromjson(obj)
