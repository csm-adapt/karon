import pytest
from convey.tree.operational import OpNode
from convey.tree import (PreorderTree,
                         PostorderTree,
                         InorderTree,
                         BreadthTree)


##### Test OpNode #####
def test_node_creation():
    node = OpNode(contents=3.1415)
    assert node.contents == 3.1415
    assert node.readable()
    assert node.writeable()


def test_readable(initialize):
    def get_readable():
        node = OpNode()
        assert node.readable()
        assert node.writeable()

    def set_readable():
        node = OpNode(readable=False)
        assert not node.readable()
        assert node.writeable()
        node.readable(True)
        assert node.readable()
        assert node.writeable()

    get_readable()
    set_readable()


def test_writeable(initialize):
    def get_writeable():
        node = OpNode()
        assert node.writeable()
        assert node.readable()

    def set_writeable():
        node = OpNode(writeable=False)
        assert not node.writeable()
        assert node.readable()
        node.writeable(True)
        assert node.writeable()
        assert node.readable()

    get_writeable()
    set_writeable()


def test_node_get_parent():
    node = OpNode()
    assert node.parent is None


def test_node_set_parent():
    def parent_good():
        parent = OpNode()
        child = OpNode()
        parent.add_child(child)
        child.parent = parent
        assert child.parent == parent

    def parent_is_self():
        parent = OpNode()
        child = parent
        try:
            parent.add_child(child)
        except ValueError:
            pass
        except:
            assert False, "A child cannot be its own parent."

    def parent_is_child():
        parent = OpNode()
        child = OpNode()
        grandchild = OpNode()
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
    child = OpNode("child")
    parent = OpNode("parent")
    parent.add_child(child)
    assert parent.contents == "parent"
    assert parent._children[0].contents == "child"


def test_node_remove_child():
    child = OpNode("child")
    parent = OpNode("parent")
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
    A, B, C, D, E, F, G, H, I = [OpNode(contents=c) for c in 'ABCDEFGHI']
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


def test__get_nodes(initialize):
    root = initialize['root']
    for node in PreorderTree(root):
        if node.contents == 'D':
            node.writeable(False)
        if node.contents == 'G':
            node.readable(False)
    results = root._get_nodes('preorder')
    expected = {
        'nodes': 'BADCEGHI',
        'readable': 'BADCE',
        'writeable': 'BAGHI'
    }
    join = lambda nlist: ''.join([n.contents for n in nlist])
    assert join(results['nodes']) == expected['nodes'], \
        'Node order does not match Preorder tree.'
    assert join(results['readable']) == expected['readable'], \
        'Readable node list does not match expected.'
    assert join(results['writeable']) == expected['writeable'], \
        'Writeable node list does not match expected.'


def test_gets(initialize):
    root = initialize['root']
    for node in PreorderTree(root):
        ch = node.contents
        node.contents = {
            'upper': ch.upper(),
            'lower': ch.lower()
        }
    upper = root.gets(lambda n: n.contents['upper'], order='preorder')
    lower = root.gets(lambda n: n.contents['lower'], order='postorder')
    expected = {
        'upper': 'BADCEGHI',
        'lower': 'acedbihg'
    }
    join = lambda chlist: ''.join(chlist)
    assert join(upper) == expected['upper']
    assert join(lower) == expected['lower']


def test_puts(initialize):
    def append_parent(node):
        node.contents = node.contents + node.parent.contents
    root = initialize['root']
    root.puts(append_parent, order='postorder')
    result = ''.join([n.contents for n in PostorderTree(root)])
    expected = 'ABCDEDDBBFIHHGGFF'
    assert result == expected
