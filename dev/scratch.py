# check if a dictionary can be used as a key in another dict.
k = {"a": 1, "b": 2}
d = {k: "a1b2"} # no.

# petname instead of UID
from petname import generate
generate(3)

# check if two lists are equal
[1] == [1]

# check petname
import numpy as np
from petname import adjectives, adverbs, names

def number_at_confidence(count, confidence):
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    return np.log(confidence)/(np.log(count-1) - np.log(count))

def probability_of_clash(count, draws):
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    return 1 - np.exp((draws-1)*(np.log(count-1) - np.log(count)))

print(f"Number of adverbs: {len(adverbs)}")
print(f"Number of adjectives: {len(adjectives)}")
print(f"Number of names: {len(names)}")

probabilityAllUnique = 0.999999
for nadv in range(4):
    label = '-'.join(nadv*['adverb'] + ['adjective', 'name'])
    count = len(adverbs)**nadv * len(adjectives) * len(names)
    print(f"{label}: {count:,} ({int(np.log2(count))} bits)")
    # p = (1 - 1/count)^(n-1)
    # ln p/ln((count - 1)/count) = n
    nUnique = np.log(probabilityAllUnique)/(np.log(count-1) - np.log(count))
    print(f"{int(nUnique):,} unique with {100*probabilityAllUnique}% confidence")
    print("--")

number_at_confidence(205184, 0.999)
probability_of_clash(205184, 207)

# json serialization
import json

class Foo:
    def __init__(self):
        self.__key = "private"

    def tojson(self):
        return {"key": self._key}

foo = Foo()
json.dumps(foo, default=lambda o: o.__dict__)

class Bar(Foo, list):
    def __init__(self, *args, **kwds):
        Foo.__init__(self)
        list.__init__(self, *args, **kwds)

    def tojson(self):
        rval = Foo.tojson(self)
        rval["contents"] = json.JSONEncoder().default(self)
        return rval

bar = Bar()
bar.extend(range(5))
bar
bar.__dict__
json.dumps(bar, default=lambda o: o.__dict__)

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if "tojson" in dir(o):
            return o.tojson()
        return json.JSONEncoder.default(self, o)

json.dumps(bar, cls=CustomEncoder)
bar.tojson()

# abstract classes
from abc import ABC, abstractmethod, abstractclassmethod
from collections.abc import Hashable, MutableMapping, MutableSet, MutableSequence
import json
from petname import generate
from functools import partial
generator = partial(generate, words=3)
uuid = lambda: "-".join([generator(), "meets", generator()])


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


class UniqueID(Hashable, Serializable):
    def __init__(self, uid=None):
        if uid is None:
            self.__uid = uuid()
        elif isinstance(uid, UniqueID):
            self.__uid = uid.uid
        else:
            self.__uid = uid

    def __hash__(self):
        return hash(self.__uid)

    @property
    def uid(self):
        return self.__uid

    def tojson(self):
        return {
            "uid": self.uid
        }

    @classmethod
    def fromjson(cls, obj):
        return cls(obj.get("uid", None))


uid = UniqueID()
uid.__dict__
UniqueID.fromjson(uid.tojson()).__dict__
uid.dumps()

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


named = Named()
named.add("abc")
named.__dict__
Named.fromjson(named.tojson()).__dict__
named.dumps()

class Attribute(Named, UniqueID, Serializable):
    def __init__(self, value=None, names=set(), uid=None):
        if isinstance(value, Attribute):
            obj = value
            value = obj.value
            names = obj.names
            uid = obj.uid
        UniqueID.__init__(self, uid=uid)
        Named.__init__(self, names=names)
        self.value = value

    def __hash__(self):
        return UniqueID.__hash__(self)

    def __contains__(self, obj):
        return ((obj == self) or
                (obj == self.uid) or
                (Named.__contains__(self, obj)))

    def __le__(self, rhs):
        return hash(self) <= hash(rhs)

    def __ge__(self, rhs):
        return hash(self) >= hash(rhs)

    def tojson(self):
        rval = dict()
        rval.update(UniqueID.tojson(self))
        rval.update(Named.tojson(self))
        rval.update({"value": self.value})
        return rval

    @classmethod
    def fromjson(cls, data):
        uid = UniqueID.fromjson(data)
        names = Named.fromjson(data)
        return  cls(value = data.get("value", None),
                    names = names,
                    uid = uid.uid)


attr = Attribute()
attr.__dict__
attr.add("abc")
attr.tojson()
a2 = Attribute.fromjson(attr.tojson())
a2.tojson()
a2 == attr
a2 is attr
hash(a2)
hash(attr)
a2 > attr
hash(a2) == hash(attr)

a3 = Attribute(a2)
a3 == a2
a3 is a2
hash(a3) == hash(a2)
a3.tojson()

attr in attr
attr.uid in attr
'abc' in attr
'def' in attr

rval = set().add('foo')
print(rval)

Attribute.loads(a3.dumps()).tojson()

class AttributeSet(MutableSet, Serializable):
    def __init__(self, items=set()):
        self.attributes = set(items)

    def get(self, obj):
        """
        Searches the AttributeSet for all entries matching `obj`.
        This always returns a list of Attributes, even if only one matching
        Attribute is found.

        :returns: list of Attribute objects.
        """
        if isinstance(obj, Attribute):
            return [obj] if obj in self.attributes else []
        else:
            return [k for k in self.attributes if obj in k]

    def __contains__(self, obj):
        return obj in self.attributes

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def add(self, obj):
        """
        All objects added to an AttributeSet must be Attributes.
        If `obj` is not an Attribute instance, an Attribute instance
        will be created with `obj` as the name of the attribute, e.g.
        :python:`Attribute(names=[obj])`. This differs from python's
        `set.add` method, which returns `None`.

        :returns: A reference to the added Attribute.
        """
        if not isinstance(obj, Attribute):
            obj = Attribute(names=[obj])
        self.attributes.add(obj)
        return obj

    def discard(self, obj):
        """
        Since all objects in an AttributeSet must be Attributes, any
        attribute in which `obj` is found are removed.
        """
        keys = self.get(obj)
        for attr in keys:
            self.attributes.discard(attr)

    def set(self, obj, value, setall=False):
        """
        Sets the value of the attribute matching `obj` to `value`.
        If no such attribute matches, a new attribute named `obj` is
        created and the value set.

        :returns: Reference to the Attribute(s) whose value(s) is/are set.
        """
        attrs = self.get(obj)
        # What happens if more than one attribute matches?
        if len(attrs) > 1:
            if setall:
                return [self.set(attr, value) for attr in attrs]
            else:
                raise KeyError(f"{len(attrs)} attributes found that match {obj}.")
        try:
            # One or zero matching attributes found.
            attr = attrs[0]
        except IndexError:
            # No matching attribute found: create a new Attribute.
            attr = self.add(Attribute(names=[obj]))
        # set the attribute
        attr.value = value
        return attr

    def tojson(self):
        return [attr.tojson() for attr in self.attributes]

    @classmethod
    def fromjson(cls, data):
        return cls(items=[Attribute.fromjson(pkg) for pkg in data])


alist = AttributeSet()

alist.attributes

alist.set("abc", 1.23).tojson()
alist.set("def", 4.56).tojson()

[attr.tojson() for attr in alist]

AttributeSet.loads(alist.dumps()).tojson()

# ##### SQL operations ##### #
import sqlite3
import os, sys
import shutil

os.curdir
os.path.abspath(os.curdir)
os.chdir('tests/data')
os.path.abspath(os.curdir)

shutil.copyfile("test.db", "delme.db")

conn = sqlite3.connect("delme.db")

conn.execute("INSERT INTO uid (ID, DATE) VALUES ('foo-bar', datetime('now'))")
conn.execute("INSERT INTO uid (ID, DATE) VALUES('freely-fleeting-fox-meets-fiery-fragrant-skink', datetime('now'))")
conn.commit()

cursor = conn.execute("SELECT * FROM uid")
for row in cursor:
    print(row)

cursor = conn.execute("SELECT ID FROM uid WHERE ID LIKE 'foo%'")
list(cursor)
cursor = conn.execute("SELECT ID FROM uid WHERE ID LIKE 'bar%'")
list(cursor)

conn.execute("INSERT INTO uid (ID, DATE) VALUES('goofily-grunting-gibon-meets-poorly-positioned-panda', datetime('now'))")

list(conn.execute("SELECT * FROM uid"))

list(conn.execute("SELECT name FROM sqlite_master WHERE type='table';"))


conn.commit()
conn.close()

# ##### functions ##### #
def foo(bar):
    name = bar
    print(f"{name}")

type(foo)
foo.__dict__


# ##### UserDict/MutableMapping as dict instances? ##### #
from collections import UserDict
from collections.abc import MutableMapping


class MyDict(UserDict):
    pass


isinstance(MyDict(), dict)


class MyMutableMap(MutableMapping):
    def __init__(self, data=dict()):
        self.data = dict(data)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


isinstance(MyMutableMap(), dict)


# ##### networkx ##### #
import networkx as nx

dg = nx.DiGraph()
dg.add_edges_from([
    (1, 3),
    (1, 4),
    (4, 6),
    (4, 7),
    (7, 10),
    (10, 11),
    (10, 12),
    (2, 4),
    (2, 5),
    (5, 8),
    (5, 9),
    (8, 10)
])

list(nx.dfs_preorder_nodes(dg, source=7))
list(nx.dfs_preorder_nodes(dg, source=8))

list(dg.predecessors(10))
