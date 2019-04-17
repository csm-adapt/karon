__all__ = ["Node", "BinaryNode",
           "Tree",
           "PreorderTree", "NLRTree",
           "InorderTree", "LNRTree",
           "PostorderTree", "LRNTree",
           "BreadthTree",
           "empty_like"]

class Node(object):
    def __init__(self, contents: object = None) -> object:
        """
        Node to store an object in a tree.

        :param contents: The contents that this node contains.
        :type contents: object
        """
        self._parent = None
        self._children = []
        self._contents = contents

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = value

    @property
    def parent(self):
        return getattr(self, '_parent', None)

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, Node):
            raise ValueError("A parent node must be itself a Node.")
        parent.add_child(self)

    @property
    def children(self):
        return self._children

    def add_child(self, child):
        # ensure the child is a Node
        if not isinstance(child, Node):
            raise ValueError("A child must be itself a Node.")
        # check that the child is not it's own descendent
        # In a post-order tree (LRN tree), the root node is reported
        # last. Therefore, if self is the last node in the LRN tree,
        # then self is the root node. If self is found in either the
        # left or the right branch, then self is its own descendent.
        descendents = [person for person in PostorderTree(self)][:-1]
        if self in descendents:
            raise ValueError("A child cannot be in its own line of descent.")

        # a child cannot be its own sibling. This is not an error--the child
        # is already there, which is what the user wanted in the first place.
        for sibling in self._children:
            if sibling is child:
                return
        # add child
        child._parent = self
        self._children.append(child)

    def remove_child(self, orphan):
        for i in reversed(range(len(self._children))):
            if self._children[i] is orphan:
                del self._children[i]


def BinaryNode(Node):
    def __init__(self, contents=None):
        super().__init__(contents=contents)
        self._children = [None, None]

    @property
    def left(self):
        return self._children[0]

    @left.setter
    def left(self, child):
        if child is self._children[0]:
            return
        del self._children[0]
        super().add_child(child)
        self._children = list(reversed(self._children))

    @property
    def right(self):
        return self._children[1]

    @right.setter
    def right(self, child):
        if child is self._children[1]:
            return
        del self._children[1]
        super().add_child(child)

    def add_child(self, child):
        raise NotImplementedError(
            "Binary nodes have a fixed number of child nodes")

    def remove_child(self, orphan):
        if orphan is self.left:
            del self._children[0]
            self._children[0] = None
        elif orphan is self.right:
            del self._children[1]
            self._children[1] = None


class Tree(object):
    def __init__(self, root=None):
        self.root = root

    @property
    def root(self):
        return getattr(self, '_root', None)

    @root.setter
    def root(self, root):
        if not isinstance(root, Node):
            contents = root
            self._root = Node(contents)
        else:
            self._root = root


class PreorderTree(Tree):
    def __init__(self, root=None):
        super().__init__(root)

    def __iter__(self):
        yield self.root
        for child in self.root._children:
            for nextgen in PreorderTree(child):
                yield nextgen


NLRTree = PreorderTree


class InorderTree(Tree):
    def __init__(self, root=None, split=0):
        super().__init__(root)
        self._split = split

    @property
    def split(self):
        if self._split < 0:
            return max(0, len(self.root._children) + self._split)
        else:
            return self._split + 1

    @split.setter
    def split(self, split):
        self._split = split

    def __iter__(self):
        split = self.split
        for left in self.root._children[:split]:
            for nextgen in InorderTree(left, split=self._split):
                yield nextgen
        yield self.root
        for right in self.root._children[split:]:
            for nextgen in InorderTree(right, split=self._split):
                yield nextgen


LNRTree = InorderTree


class PostorderTree(Tree):
    def __init__(self, root=None):
        super().__init__(root)

    def __iter__(self):
        for child in self.root._children:
            for nextgen in PostorderTree(child):
                yield nextgen
        yield self.root


LRNTree = PostorderTree


class BreadthTree(Tree):
    def __init__(self, root=None):
        super().__init__()
        if isinstance(root, (list, tuple)):
            contents = list(root)
        else:
            contents = [root]
        for box in contents:
            if not isinstance(box, Node):
                raise ValueError(
                    "A BreadthTree can only be constructed of Nodes.")
        self.root.contents = contents

    def __iter__(self):
        # create root that combines all children, then create
        # children-of-children
        nextGeneration = sum([box.children for box in self.root.contents], [])
        if nextGeneration != []:
            nextGeneration = BreadthTree(nextGeneration)
        for parent in self.root.contents:
            yield parent
        for child in nextGeneration:
            yield child


def empty_like(root):
    """
    Creates an empty collection of nodes that mimic the structure
    found in root.

    :param root: Subtree to be duplicated.
    :return: Empty structure that matches the structure of the
        template tree.
    """
    top = Node()
    for child in root.children:
        top.add_child(empty_like(child))
    return top
