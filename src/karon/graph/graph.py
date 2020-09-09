#
# The ability to map the trajectory of a material's process is central to
# understanding the properties of that material. With only very basic
# information about the origin of a material, such a map can be made using
# a directed acyclic graph.
#

import copy
import networkx as nx
from .attributes import Attributes


class Graph(nx.DiGraph):
    def __init__(self):
        super().__init__()
