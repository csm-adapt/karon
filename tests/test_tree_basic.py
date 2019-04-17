import pytest
from karon.tree import Node
from karon.tree import (PreorderTree,
                        PostorderTree,
                        InorderTree,
                        BreadthTree)
from karon.tree import empty_like


##### Test Node Properties #####

def test_node_creation():
    node = Node(contents=3.1415)
    assert node.contents == 3.1415


def test_node_get_parent():
    node = Node()
    assert node.parent is None


def test_node_set_parent():
    def parent_good():
        parent = Node()
        child = Node()
        parent.add_child(child)
        child.parent = parent
        assert child.parent == parent

    def parent_is_self():
        parent = Node()
        child = parent
        try:
            parent.add_child(child)
        except ValueError:
            pass
        except:
            assert False, "A child cannot be its own parent."

    def parent_is_child():
        parent = Node()
        child = Node()
        grandchild = Node()
        parent.add_child(child)
        child.add_child(grandchild)
        try:
            child.parent = grandchild
        except ValueError:
            pass
        except:
            assert False, "A child's parent cannot be its own child."

    parent_good()
    parent_is_self()
    parent_is_child()


def test_node_add_child():
    child = Node("child")
    parent = Node("parent")
    parent.add_child(child)
    assert parent.contents == "parent"
    assert parent._children[0].contents == "child"


def test_node_remove_child():
    child = Node("child")
    parent = Node("parent")
    parent.add_child(child)
    parent.remove_child(child)
    assert parent._children == []


##### Test Tree #####
@pytest.fixture
def initialize():
    # Tree structure
    #
    #       .F.
    #     .B.  G.
    #    A  .D.  H.
    #      C   E   I
    #
    A, B, C, D, E, F, G, H, I = [Node(contents=c) for c in 'ABCDEFGHI']
    # left
    F.add_child(B)
    B.add_child(A)
    B.add_child(D)
    D.add_child(C)
    D.add_child(E)
    # right
    F.add_child(G)
    G.add_child(H)
    H.add_child(I)
    return {
        'nodes': (A, B, C, D, E, F, G, H, I),
        'root': F
    }


def finalize():
    pass


def test_preorder_tree(initialize):
    init = initialize
    tree = PreorderTree(init['root'])
    result = ''.join([n.contents for n in tree])
    expected = 'FBADCEGHI'
    assert result == expected, '{} != {}'.format(result, expected)
    finalize()


def test_inorder_tree(initialize):
    init = initialize
    tree = InorderTree(init['root'])
    result = ''.join([n.contents for n in tree])
    expected = 'ABCDEFIHG'
    assert result == expected, '{} != {}'.format(result, expected)
    finalize()


def test_postorder_tree(initialize):
    init = initialize
    tree = PostorderTree(init['root'])
    result = ''.join([n.contents for n in tree])
    expected = 'ACEDBIHGF'
    assert result == expected, '{} != {}'.format(result, expected)
    finalize()


def test_breadth_tree(initialize):
    init = initialize
    tree = BreadthTree(init['root'])
    result = ''.join([n.contents for n in tree])
    expected = 'FBGADHCEI'
    assert result == expected, '{} != {}'.format(result, expected)
    finalize()


def test_empty_like(initialize):
    init = initialize
    copy = empty_like(init['root'])
    for ch,node in zip('ABCDEFIHG',
                       InorderTree(copy)):
        node.contents = ch
    result = ''.join(n.contents for n in PostorderTree(copy))
    expected = 'ACEDBIHGF'
    assert result == expected, '{} != {}'.format(result, expected)
    finalize()
