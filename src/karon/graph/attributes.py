#
# Object that is a hashable attribute of node in the graph
#

import logging
_logger = logging.getLogger(__name__)

from ..base import UniqueID, Named, Serializable
from ..base.util import ensure_iterable
from collections.abc import MutableSet

class Attribute(Named, UniqueID, Serializable):
    """
    Attribute used to hold information in the node of a graph. Each
    attribute has a unique ID, any number of names/synonyms, and a value.

    Attributes can be identified by their `Attribute.uid` or by any one
    of the synonymous `Attribute.names`.

    Attributes are JSON serializable.

    Examples
    ========

    :python:```
    # create an empty Attribute
    attr = Attribute() # creates an attribute with a unique ID.

    # create an unnamed attribute with value 1.234
    attr = Attribute(value=1.234)

    # create a named attribute with value 1.234
    attr = Attribute("foo", 1.234)
    attr = Attribute(["foo"], 1.234) # equivalent
    ```
    """
    def __init__(self, names=set(), value=None, uid=None):
        if isinstance(names, Attribute):
            obj = names # give it a more reasonable name
            value = obj.value
            names = obj.names
        elif isinstance(names, dict):
            kwds = names # give it a more reasonable name
            value = kwds.get("value", None)
            names = kwds.get("names", set())
            uid = kwds.get("uid", None)
        UniqueID.__init__(self, uid=uid)
        Named.__init__(self, names=ensure_iterable(names))
        self.value = value

    def __hash__(self):
        return UniqueID.__hash__(self)

    def __contains__(self, obj):
        return ((obj == self) or
                (obj == self.uid) or
                (Named.__contains__(self, obj)))

    # def __le__(self, rhs):
    #     return hash(self) <= hash(rhs)
    #
    # def __ge__(self, rhs):
    #     return hash(self) >= hash(rhs)

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


class AttributeSet(MutableSet, Serializable):
    """
    AttributeSet contains any number of Attributes with the same name,
    but only one unique Attribute, as defined by its unique ID.

    Examples
    ========

    :python:```
    # create an empty list
    alist = AttributeSet()

    # create a list of Attributes from a list of names, each with a
    # unique ID
    names = ["hello", "world"]
    alist = AttributeSet(names)

    # from a JSON-formatted file
    with open("myfile.json") as ifs:
        alist = AttributeSet.load(ifs)

    # write to a JSON formatted-file
    with open("myfile.json", "w") as ifs:
        alist.dump(ifs)

    # add a new attribute to the list
    alist.add("name") # a new Attribute named "name"

    # add a new attribute to the list and set the value to 1.234
    alist.add("name").value = 1.234

    # set an attribute named "foo"
    alist.set("foo", 1.234) # if only one Attribute is named "foo"
    alist.set("foo", 1.234, setall=True) # multiple Attributes named "foo"
    ```
    """
    def __init__(self, items=set()):
        self.attributes = set()
        for attr in items:
            self.add(attr)

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
        return any([(obj in attr) for attr in self.attributes])

    def __iter__(self):
        return iter(self.attributes)

    def __len__(self):
        return len(self.attributes)

    def union(self, aset):
        """
        Returns the union of the objects in this AttributeSet and in
        `aset`.

        :param aset: The other set which which to form the union.
        :type aset: AttributeSet

        :returns: The union of the two sets.
        :rtype: AttributeSet
        """
        rval = AttributeSet(aset)
        for attr in self:
            try:
                rval.add(attr)
            except ValueError:
                pass
        return rval

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
            obj = Attribute(names=obj)
        if obj in self:
            raise ValueError("Cannot add a duplicate Attribute. "
                             f"Offending UID: {obj.uid}.")
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
