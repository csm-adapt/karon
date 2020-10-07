#
# Algorithms to work with graphs
#

from ..base.util import ensure_iterable
import networkx as nx
from copy import deepcopy

class traverse:
    #    (1)   (2)
    #   /   \ /   \
    # (3)  (4)    (5)
    #     /  \    /  \
    #   (6) (7) (8)  (9)
    #         \ /
    #        (10)
    #        /  \
    #     (11) (12)

    # from (1): [1, 3, 4, 6, 7, 10, 11, 12]
    # from (2): [2, 4, 6, 7, 10, 11, 12, 5, 8, 9]
    preorder = nx.algorithms.dfs_preorder_nodes
    nlr = nx.algorithms.dfs_preorder_nodes

    # from (1): [3, 6, 11, 12, 10, 7, 4, 1]
    # from (2): [6, 11, 12, 10, 7, 4, 8, 9, 5, 2]
    postorder = nx.algorithms.dfs_postorder_nodes
    lrn = nx.algorithms.dfs_postorder_nodes


def roots(dg):
    """
    Returns the roots from the directed graph, `dg`.

    Parameters
    ==========
    :param dg: Directed graph.
    :type dg: nx.DiGraph

    :returns: List of karon.graph.Nodes
    """
    return [n for n,d in dg.in_degree if d==0]


def aggregate(dg, source=None):
    """
    Aggregate attributes along the graph. The graph is modified in place.
    All information is passed between nodes such that the parent initiates
    the communication request and the child accepts/rejects the request.

    :param dg: Directed graph connecting the nodes.
    :type dg: networkx.DiGraph
    :param source: (optional) Node (or Nodes) to start the search. By default
        this is all nodes of in-degree 0 (no predecessor nodes).
    :type source: one-or-more `karon.graph.Node`

    :returns: Reference to the graph
    """
    if source is None:
        source = roots(dg)
    source = ensure_iterable(source)
    # for every root...
    for src in source:
        # start at the leaf nodes...
        for parent in traverse.postorder(dg, src):
            # parent initiates communication request to the child nodes...
            for child in dg.successors(parent):
                # add each attribute from the child node into the parent.
                for attr in child.attrs:
                    try:
                        parent.attrs.add(attr)
                    except ValueError:
                        pass
    return dg


def propagate(dg, source=None):
    """
    Propagates attributes along the graph. The graph is modified in place.
    All information is passed between nodes such that the parent initiates
    the communication request and the child accepts/rejects the request.

    :param dg: Directed graph connecting the nodes.
    :type dg: networkx.DiGraph
    :param source: (optional) Node (or Nodes) to start the search. By default
        this is all nodes of in-degree 0 (no predecessors, i.e. root nodes)
        and gemel knots (where two-or-more trees join, e.g. a diamond).
    :type source: one-or-more `karon.graph.Node`

    :returns: Reference to the graph.
    """
    if source is None:
        source = roots(dg)
    source = ensure_iterable(source)
    # propagation along gemels (trees that merge, e.g. diamond structures)
    # must propagate from the "right" branch, which would otherwise be
    # skipped.
    gemels = [s for n,d in dg.in_degree if d>1 for s in dg.predecessors(n)]
    # source = source.union(gemels)
    # for every root...
    for src in list(source) + list(gemels):
        # start at the leaf nodes...
        for parent in traverse.preorder(dg, src):
            # parent initiates communication request to the child nodes...
            for child in dg.successors(parent):
                # add each attribute from the parent into the child.
                for attr in parent.attrs:
                    try:
                        child.attrs.add(attr)
                    except ValueError:
                        pass
    return dg


def disseminate(dg, source=None):
    """
    Disseminates information from parents and children up-and-down the graph.

    To simply call popagation and aggregate would result in all nodes sharing
    a common (and complete) set of Attributes, including non-descendent nodes.
    Therefore rather than a simple aggregation/propagation, aggregate on a
    copy of the graph and propagate on another copy of the graph, then take
    the union of the respective nodes. This ensures that predecessor nodes
    only contain Attributes of descendents and successor nodes only contain
    Attributes from their predecessors.

    :param dg: Directed graph connecting the nodes.
    :type dg: networkx.DiGraph
    :param source: (optional) Node (or Nodes) from which to start. By default
        this is all nodes of in-degree 0 (no predecessors, i.e. root nodes).

    :returns: Reference to the graph.
    """
    agg = aggregate(deepcopy(dg))
    prop = propagate(deepcopy(dg))
    for n,a,p in zip(traverse.preorder(dg),
                     traverse.preorder(agg),
                     traverse.preorder(prop)):
        n.attrs.union(a.attrs.union(p.attrs))
    return dg
