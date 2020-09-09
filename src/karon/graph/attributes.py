#
# Object that is a hashable attribute of node in the graph
#

import copy

import logging
_logger = logging.getLogger(__name__)

# use petnames as the uuid
try:
    from petname import generate
    from functools import partial
    uuid = partial(generate, words=5)
except:
    _logger.info("Failed to load requirements for human readable UIDs.")
    from uuid import uuid4 as uuid


class Hashable:
    def __init__(self):
        """Hashable object"""
        self.__key = str(uuid())

    def __hash__(self):
        return hash(self.__key)

    def __repr__(self):
        return self.__key

    def __str__(self):
        return self.__key

    def tojson(self):
        return {"key": self.__key}

    @classmethod
    def fromjson(cls, data):
        rval = cls()
        rval.__key = data["key"]
        return rval

    # comparison operators
    def __lt__(self, rhs):
        return hash(self) < hash(rhs)

    def __le__(self, rhs):
        return hash(self) <= hash(rhs)

    def __eq__(self, rhs):
        return hash(self) == hash(rhs)

    def __ne__(self, rhs):
        return hash(self) != hash(rhs)

    def __ge__(self, rhs):
        return hash(self) >= hash(rhs)

    def __gt__(self, rhs):
        return hash(self) > hash(rhs)


class Attributes(dict, Hashable):
    class Key(list, Hashable):
        def __new__(cls, *args, **kwds):
            try:
                if isinstance(args[0], Attributes.Key):
                    return copy.deepcopy(args[0])
            except IndexError:
                pass
            return list.__new__(cls)

        def __init__(self, *args, **kwds):
            """
            Special hashable object to be used as a key in a hashmap (dictionary).

            :param args: (optional) The type of the first argument determines the
                behavior of the constructor.
                1. If `args` is empty, a new AttributeKey is created.
                2. If `args[0]` is an AttributeKey instance, then a duplicate of
                   the key is created. All subsequent arguments are ignored.
                3. If `args` is not empty and `args[0]` is not an AttributeKey,
                   then the arguments are treated as alternative names.
            :param kwds: (optional) Keywords passed to the base class.

            Examples
            --------
            >>> repr(AttributeKey())
            '3315985523384268967: []'

            >>> repr(AttributeKey("hello", "world"))
            '-4982838445653643589: ["hello", "world"]'

            >>> repr(AttributeKey(("hello", "world")))
            '-6189777134337509944: [("hello", "world")]'
            """
            Hashable.__init__(self)
            try:
                if isinstance(args[0], Attributes.Key):
                    return
            except IndexError:
                pass
            # note the missing *args. If the user wants to specify mul...
            list.__init__(self, args, **kwds)

        def __contains__(self, value):
            return (value == Hashable.__str__(self)) or \
                   list.__contains__(self, value)

        def __hash__(self):
            return Hashable.__hash__(self)

        def __str__(self):
            return self.__repr__()

        def __repr__(self):
            return f"{Hashable.__str__(self)}: {list.__repr__(self)}"

        def tojson(self):
            rval = Hashable.tojson(self)
            rval["contents"] =

        @property
        def name(self):
            return Hashable.__str__(self)

    def __new__(cls, *args, **kwds):
        try:
            if isinstance(args[0], Attributes):
                return copy.deepcopy(args[0])
        except IndexError:
            pass
        return dict.__new__(cls)

    def __init__(self, *args, **kwds):
        """
        Attributes dictionary. Keys are converted to AttributeKey objects.
        Any value objects are left unchanged.

        :param args: (optional) The type of the first argument determines the
            behavior of the constructor.
            1. If `args` is empty, a new Attributes object is created.
            2. If `args[0]` is an Attributes instance, then a duplicate of
               the map is created. All subsequent arguments are ignored.
        :param kwds: (optional) Keywords passed to the base class.
        """
        Hashable.__init__(self)
        try:
            if isinstance(args[0], Attributes):
                return
        except IndexError:
            pass
        dict.__init__(self, *args, **kwds)
        keys = list(self.keys())
        for k in keys:
            dict.__setitem__(self, Attributes.Key(k),
                             dict.__getitem__(self, k))
            dict.__delitem__(self, k)

    def __hash__(self):
        return Hashable.__hash__(self)

    def __contains__(self, key):
        return any([(key in k) for k in self])

    def __str__(self):
        return dict.__str__(self)

    def __repr__(self):
        return dict.__repr__(self)

    def __delitem__(self, key):
        keys = self.get_key(key)
        for k in keys:
            dict.__delitem__(self, k)

    def __getitem__(self, key):
        """
        Since multiple values may share the same key label, this will return
        a list of matching values, even if only one item is found.
        """
        keys = self.get_key(key)
        return [dict.__getitem__(self, k) for k in keys]

    def __setitem__(self, key, value):
        keys = self.get_key(key)
        if len(keys) > 1:
            raise KeyError(f"Multiple Attributes found that match {key}.")
        try:
            k = keys[0]
        except IndexError:
            k = Attributes.Key(key)
        dict.__setitem__(self, k, value)

    def get_key(self, key):
        """
        Returns a list of Attribute Keys that match "key," or an empty list
        if none are found.
        """
        # If key were an Attributes.Key, then it is possible that the
        # user provide an invalid key. This will raise a KeyError. If the
        # user provides an invalid/unfound UID or alternate name, this returns
        # an empty list. This behavior is inconsistent. Choose one or the
        # other.
        # Pro/cons: All codes that use Attributes should count on handling
        # zero, one, or more returned results. An empty list does not break
        # this coding paradigm and is currently my best idea.
        if isinstance(key, Attributes.Key):
            # check for Attributes.Key object.
            return [key] if key in self else []
        else:
            # the key provided is the hash or an alternative name
            # Names are not necessarily unique, so multiple hashes may
            # correlate to the same name.
            return [k for k in self if key in k]

    def add_synonym(self, key, synonym):
        """
        Add a synonym for keys named "key".
        """
        for altnames in self.get_key(key):
            altnames.append(synonym)


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if "tojson" in dir(o):
            return o.tojson()
        return json.JSONEncoder.default(self, o)
