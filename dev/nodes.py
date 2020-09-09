# %% codecell
import json
import jsonpickle
import copy
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
from uuid import uuid4 as uuid

#    (1)   (2)
#   /   \ /   \
# (3)  (4)    (5)
#     /  \    /  \
#   (6) (7) (8)  (9)
#         \ /
#        (10)
#        /  \
#     (11) (12)
dg = nx.DiGraph()
dg.add_edges_from([(1, 3), (1, 4), \
                   (2, 4), (2, 5), \
                   (4, 6), (4, 7), \
                   (5, 8), (5, 9), \
                   (7, 10), \
                   (8, 10), \
                   (10, 11), (10, 12)])

[n for n in dg.successors(4)]
[n for n in dg.successors(2)]

# list all successors and all predecessors
# dg.succ
# dg.pred

# get successors (child nodes) following a preorder traversal
print('\n'.join([str((n, list(dg.successors(n))))
                 for n in nx.algorithms.dfs_preorder_nodes(dg)]))

# get root nodes
[n for n,d in dg.in_degree() if d==0]

# preorder tree (aggregate)
list(nx.algorithms.dfs_postorder_nodes(dg, 1))

list(nx.algorithms.dfs_postorder_nodes(dg, 2))

# postorder tree (propagate)
list(nx.algorithms.dfs_preorder_nodes(dg, 1))

list(nx.algorithms.dfs_preorder_nodes(dg, 2))

# ########################################################################### #
# The graph will contain attributes as a dictionary. However, we want to be   #
# able to do a couple things:                                                 #
#   1. In diamond-shaped graphs, as the one above, node (10) attributes would #
#      be inserted into node (2) twice: once through node (4), the other      #
#      through node (5). If each attribute is given a unique ID then this ID  #
#      can be checked before information from descendent nodes are integrated #
#      into ancestor nodes. That is, take two AttributeKeys aggregated from   #
#      child nodes. Both are named "foo". However, one may be from one        #
#      measurement, and the other from a second measurement. In this case,    #
#      both should be kept. (Repeated measurements --> reduction)             #
# ########################################################################### #

class Hashable:
    def __init__(self):
        """Hashable object"""
        self._key = str(uuid())

    def __hash__(self):
        return hash(self._key)

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

        def __hash__(self):
            return Hashable.__hash__(self)

        def __str__(self):
            return list.__str__(self)

        def __repr__(self):
            return f"{hash(self)}: {list.__repr__(self)}"

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
        keys = self.keys()
        for k in keys:
            dict.__setitem__(self, Attributes.Key(k),
                             dict.__getitem__(self, k))
            dict.__delitem__(self, k)

    def __hash__(self):
        return Hashable.__hash__(self)

    def get_key(self, key):
        """
        Returns a list of Attribute Keys that match "key," or an empty list
        if none are found.
        """
        # check for Attributes.Key object.
        if isinstance(key, Attributes.Key):
            return [key]
        # the key provided is the hash or an alternative name
        # Names are not necessarily unique, so multiple hashes may
        # correlate to the same name.
        try:
            # look for hash
            return [[k for k in self if hash(k) == key][0]]
        except IndexError:
            # check for alternative name
            return [k for k in self if key in k]

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


# Some informal testing...

attrs = Attributes(foo=1, bar=2, baz=3)


attrs

attrs[6644245320272211304]

attrs.get_key("foo")[0].append("foobar")
attrs.get_key("bar")[0].append("foobar")


attrs

attrs.get_key("foobar")


[attrs[k] for k in attrs.get_key("foobar")]


attrs[-536986052347107221]

attrs["foobar"]
attrs["baz"]


np.mean(attrs["foobar"])
np.max(attrs["baz"])
repr(list(attrs.keys())[0])

# jsonpickle does not reproduce the same object.
dup = jsonpickle.loads(jsonpickle.dumps(attrs))

dup == attrs

dup


# deepcopy makes an editable copy
dup = copy.deepcopy(attrs)

dup == attrs

dup

[x.append('foobaz') for x in dup.get_key('foobar')]
dup

attrs
