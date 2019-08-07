import pytest
from karon.tree.build import from_parent
from karon.tree.build import generate_tree
from karon.tree import NLRTree
from karon.tree import Node
from karon.tree.util import get


@pytest.fixture
def some_nodes():
    return [
        Node(contents={'name': 'a'}),
        Node(contents={'parent': 'a', 'name': 'b'}),
        Node(contents={'parent': 'b', 'name': 'c'}),
        Node(contents={'parent': 'b', 'name': 'd'}),
        Node(contents={'name': 'A'}),
        Node(contents={'parent': 'A', 'name': 'B'}),
        Node(contents={'parent': 'B', 'name': 'C'}),
        Node(contents={'parent': 'B', 'name': 'D'})
    ]


def test_from_parent(some_nodes):
    nodes = some_nodes
    # ##### usage example ##### #
    roots = from_parent(nodes, get_key='name', get_parent='parent')
    assert len(roots) == 2, \
        f"Wrong number of roots were found ({len(roots)}), expected 2. " \
        f"roots found: {roots}"
    lower, upper = roots
    # tests
    # implicit check: neither node 'a' nor 'A' have a parent,
    # therefore both are roots of their respective trees,
    # lower and upper.
    # sequence
    seq = '-'.join([n.contents['name'] for n in NLRTree(lower)])
    assert seq == 'a-b-c-d'
    seq = '-'.join([n.contents['name'] for n in NLRTree(upper)])
    assert seq == 'A-B-C-D'


def test_orphaned_from_parent(some_nodes):
    nodes = [Node(contents={'parent': 'missing', 'name': 'orphan'})] \
            + some_nodes
    roots = from_parent(nodes, get_key='name', get_parent='parent')
    actual = [n.contents['name'] for n in roots]
    expected = ['a', 'A', 'orphan']
    for name in actual:
        assert name in expected, \
            f"{name} missing from expected root nodes."
    for name in expected:
        assert name in actual, \
            f"{name} missing from root nodes read in."


def test_generate_tree(some_nodes):

    def strcmp(*transforms):
        def func(lhs, rhs):
            l = str(lhs)
            r = str(rhs)
            for t in transforms:
                l = t(l)
                r = t(r)
            return (l == r)

        return func

    nodes = some_nodes
    roots = generate_tree(
        get_nodeid=get("name"),
        get_parent=get("parent"),
        cmp = strcmp(str.strip))(nodes)
    assert len(roots) == 2, \
        f"Wrong number of roots were found ({len(roots)}), expected 2. " \
            f"roots found: {roots}"
    lower, upper = roots
    # tests
    # implicit check: neither node 'a' nor 'A' have a parent,
    # therefore both are roots of their respective trees,
    # lower and upper.
    # sequence
    seq = '-'.join([n.contents['name'] for n in NLRTree(lower)])
    assert seq == 'a-b-c-d'
    seq = '-'.join([n.contents['name'] for n in NLRTree(upper)])
    assert seq == 'A-B-C-D'
