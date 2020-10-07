#
# The ability to map the trajectory of a material's process is central to
# understanding the properties of that material. With only very basic
# information about the origin of a material, such a map can be made using
# a directed acyclic graph.
#

import networkx as nx
import types
from collections import OrderedDict
from .attributes import Attribute, AttributeSet
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


class DiGraph(nx.DiGraph):
    """Graph defining the connectivity between sets of attributes.

    This mirrors the functionality of a `networkx.DiGraph`, but contents
    are contained in Attributes and AttributeSets.
    """
    def add_edge(self, u_of_edge, v_of_edge, **attr):
        """
        Add a single edge. If `u_of_edge` and `v_of_edge` are not Node objects,
        then Node objects will be created. This introduces an edge case that
        is worth pointing out: if `u_of_edge` and `v_of_edge` are identical,
        then the node points to itself.

        If edges are added one-at-a-time, then named objects (that is, objects
        that are not `Node`s), if subsequent calls are made with the same name
        this will create unique nodes. (The uniqueness of `Nodes` is not in
        their name, but in their uid.) If all names are unique, the graph edges
        should be constructed using the `add_edges_from` method, which checks
        for uniqueness before creating nodes.

        :param u_of_edge: Node at start of edge.
        :param v_of_edge: Node at end of edge.
        :param attr: edge attributes
        :return: None
        """
        try:
            u, v = {u_of_edge, v_of_edge}
            u, v = self.add_node(u), self.add_node(v)
        except ValueError:
            u = v = self.add_node(u_of_edge)
        super().add_edge(u, v, **attr)

    def add_edges_from(self, ebunch_to_add, **attr):
        """
        Add multiple edges from a list of tuples. `ebunch_to_add` is iterated
        multiple times, so it is converted into a list if `ebunch_to_add` is
        a generator.

        Only nodes from unique elements in `ebunch_to_add` are added to the
        graph. Therefore, adding multiple nodes using this function is
        materially different than adding those same edges one-at-a-time using
        `add_edge`, that is

        ```python
            dg = DiGraph()
            uv = [("foo", "bar"), ("bar", "baz"), ("bar", "rab")]
            # this creates four new nodes
            dg.add_edges_from(uv)
            # this creates six new nodes
            for u,v in uv:
                dg.add_edge(u, v)
            # and this creates four more new nodes
            dg.add_edges_from(uv)
        ```

        because names are taken to be the names of the Nodes, but Nodes are not
        identified by their name (multiple nodes can have the same name), they
        are identified by their UID/instance.

        :param ebunch_to_add: Iterable of iterables, e.g. list of 2-tuples.
        :param attr: edge attributes
        :return: None
        """
        # convert ebunch_to_add to tuple if it is a generator
        if isinstance(ebunch_to_add, types.GeneratorType):
            ebunch_to_add = list(ebunch_to_add)
        # create a list of unique nodes
        nodes = list(set().union(*ebunch_to_add))
        # create a map between the unique nodes and the Nodes that were added
        nodes = {k:v for k,v in zip(nodes, self.add_nodes_from(nodes))}
        # add the Node objects indicated by ebunch_to_add
        super().add_edges_from(
            [(nodes[u], nodes[v]) for u, v in ebunch_to_add], **attr)

    def add_node(self, node_to_add, **attr):
        """
        Add a node. If `node_to_add` is not a Node object, then a new Node is
        created. This has some unexpected consequences compared to the
        `networkx.DiGraph`.

        ```python
            dg = DiGraph()
            node = Node("foo")
            dg.add_node(node) # dg has one node
            # adds five more nodes, all named "foo", but with unique UIDs.
            # After this, dg will have six nodes
            for _ in range(5):
                dg.add_node(Node("foo"))
            dg.add_node(node) # dg still only has six nodes.
        ```

        While this behavior is consistent with `networkx.DiGraph`, since each
        Node is a unique object, that consistency may not be immediately
        evident since all Nodes are named "foo".


        :param node_to_add: The node to add. Typically a Node or a string.
        :param attr: Node attributes.
        :return: The Node that was added. This is a reference to `node_to_add`
            if `node_to_add` is a Node, otherwise, this is the newly created
            Node.
        """
        n = node_to_add if isinstance(node_to_add, Node) else Node(node_to_add)
        super().add_node(n, **attr)
        return n

    def add_nodes_from(self, nodes_to_add, **attr):
        """
        Adds unique nodes from `nodes_to_add`. The nodes returned are
        guaranteed to be in the same order as they appeared in `nodes_to_add`.

        :param nodes_to_add: Iterable or generator of nodes to add.
        :param attr: Properties of each node.
        :return: list of nodes added to the graph.
        """
        nodes = tuple(OrderedDict.fromkeys(nodes_to_add))
        return [self.add_node(n) for n in nodes]
