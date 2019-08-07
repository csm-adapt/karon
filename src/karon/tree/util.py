__all__ = ["get", "put"]


def get(key):
    """
    Function generator to get a specific key from a node.

    :param key: The key to extract from the node.
    :type key: str
    :return: Unary function with signature func(node: Node) -> entry
    """
    def func(node):
        return node.contents.get(key, None)
    return func


def put(key, overwrite=False):
    """
        Function generator to put a specific key/value pair in a node.

        :param key: The key to access from the node.
        :type key: str
        :return: Binary function with signature func(node: Node, value) -> None
        """
    def func(node, value):
        if (key not in node.contents) or overwrite:
            node.contents[key] = value
    return func