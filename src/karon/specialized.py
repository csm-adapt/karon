__all__ = ["OpNode", "as_opnode"]


from .tree import Node
from .tree import (PreorderTree,
                        PostorderTree,
                        BreadthTree)
from .tree import empty_like


class OpNode(Node):
    def __init__(self,
                 contents=None,
                 readable: bool = True,
                 writeable: bool = True):
        """
        OpNodes (short for Operational Node), prescribes functions
        for pushing information down to child nodes or for pulling
        information from child nodes.

        :param contents, object: The object stored in the node.
        :param readable, bool: Whether this node is readable by its
            antecedents.
        :param writeable, bool: Whether this node is writeable by
            its antecedents.
        """
        super().__init__(contents)
        self._readable = bool(readable)
        self._writeable = bool(writeable)

    def _get_nodes(self, order: str):
        """
        The relationship between nodes is a tree structure. An
        unwriteable (unreadable) node renders the subsequent
        subtree unwriteable (unreadable) to predecessor nodes.
        Therefore, a list of all nodes is made based on the
        requested tree traversal order (see below). Then, the
        readability and writeability of each node is determined
        based on its own RW status and the RW status of its parent
        node.

        A dictionary is returned with the list of readable and
        writeable nodes.

        Recursive (excludes this node):
            preorder: preorder (NLR) tree
            postorder: postorder (LRN) tree
            breadth: breadth order tree

        Not recursive (children only):
            children: iterate over children

        :param order, str: See summary for options and description.
        :return:
            {
                'nodes': [list of all nodes in the requested traversal],
                'readable': [list of readable nodes],
                'readable mask': [boolean indexing to get readable nodes],
                'writeable'; [list of writeable nodes],
                'writeable mask': [boolean mask for writeable nodes]
            }
        """
        key = order.lower()
        # list of all nodes
        nodes = {
            'preorder': list(PreorderTree(self))[1:],
            'postorder': list(PostorderTree(self))[:-1],
            'breadth': list(BreadthTree(self))[1:],
            'children': self.children
        }[key]
        # subtrees
        subtree = {
            'readable': empty_like(self),
            'writeable': empty_like(self)
        }
        # if parent is not readable/writeable to its predecessors,
        # neither are its descendants.
        for node, read, write in zip(
                list(PreorderTree(self)),
                list(PreorderTree(subtree['readable'])),
                list(PreorderTree(subtree['writeable']))):
            read.contents = node.readable()
            write.contents = node.writeable()
            # The readability/writeability of the root node (self)
            # is irrelevant, because read/write operations occur on
            # the children by the parent, not on the parent by the
            # children. Therefore, only propagate the readability/
            # writeability of the parent to the child on grandchild
            # and subsequent generations of the root node.
            try:
                read.contents &= read.parent.contents
                write.contents &= write.parent.contents
            except TypeError: # if contents is None
                pass
            except AttributeError: # if parent is None
                pass
        # use these boolean trees to choose appropriate nodes
        results = {'nodes': nodes}
        for k,v in iter(subtree.items()):
            mask = {
                'preorder': list(PreorderTree(v))[1:],
                'postorder': list(PostorderTree(v))[:-1],
                'breadth': list(BreadthTree(v))[1:],
                'children': v.children
            }[key]
            results[k + ' mask'] = mask
            results[k] = [n for b,n in zip(mask, nodes) if b.contents]
        # done
        return results

    def gets(self,
             func,
             order: str = 'postorder',
             callback=None):
        """
        Apply a "gets" operation to each child node. The (optional)
        callback operation is called on the list that results, and can be
        used to reduce the results of the gets operation, e.g. calculate
        the mean, median, stdev, etc.

        The order of operations, whether recursive or not, is set
        by the `order` parameter (see below for details).

        Recursive (excludes this node):
            preorder: preorder (NLR) tree
            postorder: postorder (LRN) tree (default)
            breadth: breadth order tree

        Not recursive (children only):
            children: iterate over children

        A postorder tree is the default because in the creation of a tree
        that follows a sequential process--such as creation of samples,
        subsamples, etc.--the leaf nodes are the most recent on any
        subtree and appear first in the list of results.

        :param func: "Gets"-like function applied to each child node. This
            will typically be a function that operates on the contents of
            the node, for example, returning a specific keyed value from
            dictionary-like node contents.
        :type func: Unary function with signature `func(node: Node) -> object`
        :param order, str: (optional) The order in which to return the
            child nodes. Default: A postorder (LRN tree).
        :param callback: (optional) Signature: `f(node: Node, results)`
            Function to apply to the list of results. This can be used
            to set an attribute of the current node with a reduction
            of the properties of the descendent nodes.
        :type callback: Binary function.
        :return:
            List of the results of `func` applied to each descendant node.
        """
        results = [func(n) for n in self._get_nodes(order)['readable']]
        if callback is not None:
            callback(self, results)
        return results

    def puts(self, func, order: str = 'preorder'):
        """
        Apply a "puts" operation to each child node.

        The order of operations, whether recursive or not, is set
        by the `order` parameter (see below for details).

        Recursive (excludes this node):
            preorder: preorder (NLR) tree (default)
            postorder: postorder (LRN) tree.
            breadth: breadth order tree

        Not recursive (children only):
            children: iterate over children

        A preorder tree is the default to ensure modifications to the
        child node are performed before the grandchildren nodes;
        grandchildren before great-grandchildren, etc.

        :param func, callable: "Puts"-like function applied
            to each child node. This will typically be a function that
            operates on, or replaces, the contents of the node. Because
            this is generally destructive, no default is set.
        :type func: Unary function with signature
            `func(node: Node) -> None`
        :param order, str: (optional) The order in which to return the
            child nodes. Default: A preorder (NLR) tree.
        :return: None
        """
        for n in self._get_nodes(order)['writeable']:
            if n.writeable():
                func(n)

    def readable(self, flag: bool = None):
        """
        Get and set whether this node is readable by its predecessors.

        Upon creation of a sample that changes its fundamental properties
        relative to its predecessors, e.g. after an anneal, then
        the properties of that node, and all its descendants, should
        not be readable to predecessors

        :param flag, bool: If provided (and not None), sets whether
            (True) or not (False) pull operations should be allowed
            on this node. If not provided (or None), returns whether
            or not pull operations are allowed on this node.

        :return:
            If `flag` is None, then returns a boolean to declare
            whether (True) or not (False) pull operations are
            allowed on this node. If `flag` is not None, then
            returns None.

        Example:
            instance.readable()
            Returns whether read operations are allowed.

            instance.readable(True)
            Sets a flag so that this node can allow read operations
        """
        if flag is None:
            return self._readable
        else:
            self._readable = bool(flag)

    def writeable(self, flag: bool = None):
        """
        Get and set whether this node should allow its antecedents
        to write to it.

        :param flag, bool: If provided (and not None), sets whether
            (True) or not (False) write operations should be allowed
            on this node. If not provided (or None), returns whether
            or not push operations are allowed on this node.

        :return:
            If `flag` is None, then returns a boolean to declare
            whether (True) or not (False) write operations are
            allowed on this node. If `flag` is not None, then
            returns None.

        Example:
            instance.writeable()
            Returns whether push operations are allowed.

            instance.writeable(True)
            Sets a flag so that this node can allow push operations.
        """
        if flag is None:
            return self._writeable
        else:
            self._writeable = bool(flag)


def as_opnode(root):
    """
    Returns the tree defined at root as a tree of Operational Nodes (OpNode).
    """
    # check if all nodes are already OpNodes
    for node in PreorderTree(root):
        if not isinstance(node, OpNode):
            copy = empty_like(root, OpNode)
            for src, dst in zip(LRNTree(root), LRNTree(copy)):
                dst.contents = src.contents.copy()
                if isinstance(src, OpNode):
                    dst.writeable(src.writeable())
                    dst.readable(src.readable())
            return copy
    return root
