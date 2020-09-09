#
# Algorithms to work with graphs
#

import networkx as nx


class traverse:
    preorder = nx.algorithms.dfs_preorder_nodes
    lrn = nx.algorithms.dfs_preorder_nodes

    postorder = nx.algorithms.dfs_postorder_nodes
    nlr = nx.algorithms.dfs_postorder_nodes
