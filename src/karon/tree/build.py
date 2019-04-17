import warnings


def from_parent(nodes, key):
    """
    Builds up tree structures from a dictionary of nodes. The name of the
    parent node is given by `key` in the will-be child node contents, e.g.

        parent = node.contents[key]
        nodes[parent].add_child(node)

    Any node that does not specify a parent is the root node of its own
    tree.

    :param nodes: (dict) Nodes mapped to node name.
    :param key: (str) Content key that indicates the name of the parent
        node.
    :return: (list) Constructed trees.
    """
    roots = []
    for k,v in iter(nodes.items()):
        parent = v.contents.get(key, None)
        if parent:
            try:
                nodes[parent].add_child(v)
            except KeyError:
                warnings.warn(f"{parent} was not found in the set of "
                              f"nodes. Child will be treated as a root.")
                roots.append(v)
        else:
            roots.append(v)
    return roots
