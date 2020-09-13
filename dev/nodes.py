# %% codecell
import json
import jsonpickle
import copy
import numpy as np
import networkx as nx
from matplotlib import pyplot as plt
from uuid import uuid4 as uuid

#    (1)   (2)
#   /   \ /   \
# (3)  (4)    (5)
#     /  \    /  \
#   (6) (7) (8)  (9)
#         \ /
#        (10)
#        /  \
#     (11) (12)
dg = nx.DiGraph()
dg.add_edges_from([(1, 3), (1, 4), \
                   (2, 4), (2, 5), \
                   (4, 6), (4, 7), \
                   (5, 8), (5, 9), \
                   (7, 10), \
                   (8, 10), \
                   (10, 11), (10, 12)])

[n for n in dg.successors(4)]
[n for n in dg.successors(2)]
list(dg.predecessors(3))

# list all successors and all predecessors
# dg.succ
# dg.pred

# get successors (child nodes) following a preorder traversal
print('\n'.join([str((n, list(dg.successors(n))))
                 for n in nx.algorithms.dfs_preorder_nodes(dg)]))

# get root nodes
[n for n,d in dg.in_degree() if d==0]

# preorder tree (aggregate)
list(nx.algorithms.dfs_postorder_nodes(dg, 1))

list(nx.algorithms.dfs_postorder_nodes(dg, 2))

# postorder tree (propagate)
list(nx.algorithms.dfs_preorder_nodes(dg, 1))

list(nx.algorithms.dfs_preorder_nodes(dg, 2))

# ########################################################################### #
# The graph will contain attributes as a dictionary. However, we want to be   #
# able to do a couple things:                                                 #
#   1. In diamond-shaped graphs, as the one above, node (10) attributes would #
#      be inserted into node (2) twice: once through node (4), the other      #
#      through node (5). If each attribute is given a unique ID then this ID  #
#      can be checked before information from descendent nodes are integrated #
#      into ancestor nodes. That is, take two AttributeKeys aggregated from   #
#      child nodes. Both are named "foo". However, one may be from one        #
#      measurement, and the other from a second measurement. In this case,    #
#      both should be kept. (Repeated measurements --> reduction)             #
# ########################################################################### #
