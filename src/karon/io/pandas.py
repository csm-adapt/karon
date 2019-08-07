import pandas as pd


def to_dataframe(nodes):
    """
    Writes a list of nodes as a pandas.DataFrame.

    Parameters
    ==========
    :param nodes: List of nodes that are to be combined into a DataFrame
    :type nodes: list of karon.Node objects.
    :return: pandas.DataFrame constructed from the contents of the nodes.
    """
    result = {}
    for node in nodes:
        for key in node.contents.keys():
            result[key] = []
    keyset = set(result.keys())
    for node in nodes:
        # add all values
        for k,v in iter(node.contents.items()):
            result[k].append(v)
        # add empty field for missing values
        for k in (keyset - set(node.contents.keys())):
            result[k].append('')
    return pd.DataFrame(result)
