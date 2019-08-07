__all__ = ["generate_tree", "from_parent"]


import warnings


def generate_tree(get_nodeid, get_parent, cmp=None):
    """
    Defines the functions required to (a) extract a field from a
    node, (b) extract a field from a prospective parent node, and (c)
    compare the results to establish whether the prospective node
    is (`cmp` returns True) or is not (`cmp` returns False) the parent
    of the node.

    Example:

        def get_parent(node):
            return node.contents['parent name']
        def get_name(node):
            return node.contents['name']
        nodes = get_nodelist_from_file('foo.xlsx')
        tree = generate_tree(get_name, get_parent)(nodes)

    :param get_nodeid: Unary function that extracts a field from a Node object.
    :type get_nodeid: Unary function, signature: nodeExtract(Node).
    :param get_parent: Unary function that extracts a field from a Node object.
    :type get_parent: Unary function or None. If a unary function, the signature
        is parentID(Node)
    :param cmp: (optional) Unary function that compares the results of
        parentID and nodeExtract. Returns True if the values match,
        False otherwise.
    :return: Unary function, signature: f(array-like-of-Nodes)
    """

    def equal(lhs, rhs):
        return lhs == rhs

    def build(nodelist):
        """
        Returns the parent of the node.
        :param nodelist: List of nodes to be used to build a tree
        :return:
        """
        roots = []
        for node in nodelist:
            value = get_parent(node)
            # which nodes in "nodelist" are parents of "node"?
            parents = [n for n in nodelist if cmp(value, get_nodeid(n))]
            if len(parents) > 1:
                # TODO: Rather than return an error, compose a common parent
                #  that combines properties from the matching parent
                #  nodes. Along with the original child node
                #  these matching parents become the children to
                #  the common parent, thereby maintaining the single parent
                #  required for a tree, but establishing a connection to
                #  all matching parents.
                #  COMPLICATIONS:
                #    1. What properties do the common parent have?
                #    2. How are the matching parent attributes combined
                #       in the common parent? (list/append? reduce?)
                msg = f'{value} has more than one ({len(parents)}) matching '\
                      f'parent node: {[p.contents for p in parents]}'
                raise ValueError(msg)
            try:
                parent = parents[0]
                parent.add_child(node)
            except IndexError:
                # no parent found, therefore this node is a root node
                roots.append(node)
        return roots

    # handle positional parameters
    # handle optional parameters
    cmp = equal if cmp is None else cmp

    return build


def from_parent(nodes, get_key, get_parent):
    """
    Builds up tree structures from a dictionary of nodes. The name of the
    parent node is given by `key` in the will-be child node contents, e.g.

        parent = node.contents[key]
        nodes[parent].add_child(node)

    Any node that does not specify a parent is the root node of its own
    tree.

    :param nodes: List of nodes that are to be structured into trees
    :type nodes: List-like.
    :param get_key: Gets the identifier for each node.
    :type get_key: Unary function or string. Unary function has the signature
        `get_key(node)` and returns a hashable object. If get_key is a string,
        returns node.contents[get_key].
    :param get_parent: Gets the identifier for the parent for each node.
    :type get_parent: Unary function or string. Unary function has the signature
        `get_parent(node)` and returns a hashable object. If get_parent is a
        string, returns node.contents[get_parent]. If no parent node is
        found, then returns None.
    :return: Constructed trees.
    :rtype: list
    """
    # if get_key or get_parent are strings, then these will be interpretted
    # as the key in the Node.contents dictionary.
    if isinstance(get_key, str):
        key_str = get_key

        def get_key(node):
            return node.contents.get(key_str, None)

    if isinstance(get_parent, str):
        parent_str = get_parent

        def get_parent(node):
            return node.contents.get(parent_str, None)

    # construct a map of the nodes
    nodemap = {get_key(node): node for node in nodes}
    # construct the trees
    roots = []
    for key, node in iter(nodemap.items()):
        parent = get_parent(node)
        if parent is not None:
            try:
                nodemap[parent].add_child(node)
            except KeyError:
                warnings.warn(f"{parent} was not found in the set of "
                              f"nodes. Child will be treated as a root.")
                roots.append(node)
        else:
            roots.append(node)
    return roots
