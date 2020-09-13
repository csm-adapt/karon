from .serialize import Serializable
from collections.abc import MutableSet

class Named(MutableSet, Serializable):
    def __init__(self, names=set()):
        self.names = set(names)

    def __contains__(self, obj):
        return (obj in self.names)

    def __iter__(self):
        return iter(self.names)

    def __len__(self):
        return len(self.names)

    def add(self, obj):
        self.names.add(obj)

    def discard(self, obj):
        self.names.discard(obj)

    def tojson(self):
        return {
            "names": list(self.names)
        }

    @classmethod
    def fromjson(cls, obj):
        rval = cls(obj.get("names", []))
        return rval
