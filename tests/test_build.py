import pytest
from karon.tree.build import from_parent
from karon.tree import NLRTree
from karon.tree.operational import Node


@pytest.fixture
def some_nodes():
    return {
        'a': Node(contents={'name': 'a'}),
        'b': Node(contents={'parent': 'a', 'name': 'b'}),
        'c': Node(contents={'parent': 'b', 'name': 'c'}),
        'd': Node(contents={'parent': 'b', 'name': 'd'}),
        'A': Node(contents={'name': 'A'}),
        'B': Node(contents={'parent': 'A', 'name': 'B'}),
        'C': Node(contents={'parent': 'B', 'name': 'C'}),
        'D': Node(contents={'parent': 'B', 'name': 'D'})
    }


def test_from_parent(some_nodes):
    nodes = some_nodes
    # ##### usage example ##### #
    lower, upper = from_parent(nodes, key='parent')
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
    nodes = {
        'orphan': Node(contents={'parent': 'missing', 'name': 'orphan'}),
        **some_nodes
    }
    roots = from_parent(nodes, key='parent')
    actual = [n.contents['name'] for n in roots]
    expected = ['a', 'A', 'orphan']
    for name in actual:
        assert name in expected, \
            f"{name} missing from expected root nodes."
    for name in expected:
        assert name in actual, \
            f"{name} missing from root nodes read in."
