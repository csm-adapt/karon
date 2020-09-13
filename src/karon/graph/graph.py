#
# The ability to map the trajectory of a material's process is central to
# understanding the properties of that material. With only very basic
# information about the origin of a material, such a map can be made using
# a directed acyclic graph.
#

# import networkx as nx
from .attributes import AttributeSet
from ..base import UniqueID, Serializable


class Node(UniqueID, Serializable):
    def __init__(self, name=None, attrs=AttributeSet(), uid=None):
        """
        Node to be stored in an networkx.DiGraph.

        Parameters
        ==========
        :param name: Name of the node.
        :type name: str
        :param attrs: Set of attributes stored in the node.
        :type attrs: AttributeSet
        :param uid: Enforce the UniqueID to use for this Node. This is
            generally reserved for constructing a Node from a persistent
            resource (such as a JSON file or a string).
        :type uid: str, int, or other hashable object.
        """
        if isinstance(name, Node):
            node = name
            name = node.name
            attrs = node.attrs
        if isinstance(name, dict):
            d = name
            name = d.get("name", None)
            attrs = d.get("attrs", AttributeSet())
            uid = d.get("uid", None)
        UniqueID.__init__(self, uid=uid)
        self.name = name
        if not isinstance(attrs, AttributeSet):
            attrs = AttributeSet(attrs)
        self.attrs = attrs

    def __hash__(self):
        return UniqueID.__hash__(self)

    def __contains__(self, obj):
        return ((obj == self) or
                (obj == self.uid) or
                (obj in self.attrs))

    def tojson(self):
        rval = dict()
        rval.update(UniqueID.tojson(self))
        rval.update({
            "name": self.name,
            "attributes": self.attrs.tojson()
        })
        return rval

    @classmethod
    def fromjson(cls, pkg):
        name = pkg.get("name", None)
        attrs = AttributeSet.fromjson(pkg.get("attributes", []))
        uid = pkg.get("uid", None)
        return cls(name=name, attrs=attrs, uid=uid)
