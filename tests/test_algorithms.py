import sys
import unittest
import networkx as nx
import numpy as np
from karon.graph import roots, Node, traverse
from karon.graph import AttributeSet
from karon.graph import aggregate, propagate, disseminate

import logging
# _logger = logging.getLogger(__name__)

__author__ = "Branden Kappes"
__copyright__ = "KMMD, LLC."
__license__ = "mit"


class TestAlgorithms(unittest.TestCase):
    #    (1)   (2)
    #   /   \ /   \
    # (3)  (4)    (5)
    #     /  \    /  \
    #   (6) (7) (8)  (9)
    #         \ /
    #        (10)
    #        /  \
    #     (11) (12)
    def setUp(self):
        self.nodes = n = {
            1: Node(name="1. Ti64 powder",
                    attrs=[{"names": "Node 1", "value": "Carpenter"}]),
            2: Node(name="2. Build 123",
                    attrs=[{"names": "Node 2", "value": "Aconity"}]),
            3: Node(name="3. ICP",
                    attrs=[{"names": "Node 3", "value": 0.9}]),
            4: Node(name="4. Ti64 charge",
                    attrs=[{"names": "Node 4", "value": 50}]),
            5: Node(name="5. ASTM E8 flat",
                    attrs=[{"names": "Node 5", "value": 275}]),
            6: Node(name="6. ICP",
                    attrs=[{"names": "Node 6", "value": 0.06}]),
            7: Node(name="7. ASTM E8 flat",
                    attrs=[{"names": "Node 7", "value": 325}]),
            8: Node(name="8. ASTM E112 average grain size",
                    attrs=[{"names": "Node 8", "value": 50}]),
            9: Node(name="9. ASTM STP1203 fractography",
                    attrs=[{"names": "Node 9", "value": "path/to/fractograph.tif"}]),
            10: Node(name="10. ASTM STP1616 hot isostatic pressing",
                     attrs=[{"names": "Node 10", "value": 400}]),
            11: Node(name="11. ASTM E112 average grain size",
                     attrs=[{"names": "Node 11", "value": 100}]),
            12: Node(name="12. ASTM E606 strain-controlled fatigue",
                     attrs=[{"names": "Node 12", "value": 1234567}])
        }
        self.node_to_index = {v:k for k,v in self.nodes.items()}
        self.digraph = dg = nx.DiGraph()
        dg.add_edges_from([
            (n[1], n[3]),
            (n[1], n[4]),
            (n[4], n[6]),
            (n[4], n[7]),
            (n[7], n[10]),
            (n[10], n[11]),
            (n[10], n[12]),
            (n[2], n[4]),
            (n[2], n[5]),
            (n[5], n[8]),
            (n[5], n[9]),
            (n[8], n[10])
        ])
        self.roots = (n[1], n[2])
        self.order = {
            "preorder": [
                [1, 3, 4, 6, 7, 10, 11, 12],
                [2, 4, 6, 7, 10, 11, 12, 5, 8, 9]
            ],
            "postorder": [
                [3, 6, 11, 12, 10, 7, 4, 1],
                [6, 11, 12, 10, 7, 4, 8, 9, 5, 2]
            ]
        }
        # from matplotlib import pyplot as plt
        # plt.ioff()
        # nx.draw_planar(dg)
        # plt.show()

    def test_roots(self):
        r1, r2 = roots(self.digraph)
        self.assertIn(r1, self.roots)
        self.assertIn(r2, self.roots)

    def test_traverse(self):
        dg = self.digraph
        r1, r2 = self.roots
        # check traverse.preorder
        # r1
        nodes = traverse.preorder(dg, r1)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["preorder"][0]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # r2
        nodes = traverse.preorder(dg, r2)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["preorder"][1]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # check traverse.nlr
        # r1
        nodes = traverse.nlr(dg, r1)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["preorder"][0]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # r2
        nodes = traverse.nlr(dg, r2)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["preorder"][1]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # check traverse.postorder
        # r1
        nodes = traverse.postorder(dg, r1)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["postorder"][0]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # r2
        nodes = traverse.postorder(dg, r2)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["postorder"][1]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # check traverse.lrn
        # r1
        nodes = traverse.lrn(dg, r1)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["postorder"][0]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))
        # r2
        nodes = traverse.lrn(dg, r2)
        indices = [self.node_to_index[n1] for n1 in nodes]
        expected = self.order["postorder"][1]
        equal = [a1 == a2 for a1,a2 in zip(indices, expected)]
        self.assertTrue(all(equal))

    def test_aggregate(self):
        n = self.nodes
        dg = self.digraph
        aggregate(dg)
        allnodes = set(range(1, 13))
        for node, joint in ((n[1], (1, 3, 4, 6, 7, 10, 11, 12)),
                            (n[2], (2, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
                            (n[3], (3,)),
                            (n[4], (4, 6, 7, 10, 11, 12)),
                            (n[5], (5, 8, 9, 10, 11, 12)),
                            (n[6], (6,)),
                            (n[7], (7, 10, 11, 12)),
                            (n[8], (8, 10, 11, 12)),
                            (n[9], (9,)),
                            (n[10], (10, 11, 12)),
                            (n[11], (11,)),
                            (n[12], (12,))):
            disjoint = allnodes - set(joint)
            for index in joint:
                name = f"Node {index}"
                self.assertIn(name, node.attrs,
                    f"{name} not found in {node.dumps(indent=4)}")
            for index in disjoint:
                name = f"Node {index}"
                self.assertNotIn(name, node.attrs,
                    f"{name} found in {node.dumps(indent=4)}")

    def test_propagate(self):
        n = self.nodes
        dg = self.digraph
        propagate(dg)
        allnodes = set(range(1, 13))
        for node, joint in ((n[1], (1,)),
                            (n[2], (2,)),
                            (n[3], (1, 3)),
                            (n[4], (1, 2, 4)),
                            (n[5], (2, 5)),
                            (n[6], (1, 2, 4, 6)),
                            (n[7], (1, 2, 4, 7)),
                            (n[8], (2, 5, 8)),
                            (n[9], (2, 5, 9)),
                            (n[10], (1, 2, 4, 5, 7, 8, 10)),
                            (n[11], (1, 2, 4, 5, 7, 8, 10, 11)),
                            (n[12], (1, 2, 4, 5, 7, 8, 10, 12))):
            disjoint = allnodes - set(joint)
            for index in joint:
                name = f"Node {index}"
                self.assertIn(name, node,
                    f"{name} not found in {node.dumps(indent=4)}")
            for index in disjoint:
                name = f"Node {index}"
                self.assertNotIn(name, node,
                    f"{name} found in {node.dumps(indent=4)}")

    def test_disseminate(self):
        n = self.nodes
        dg = self.digraph
        disseminate(dg)
        allnodes = set(range(1, 13))
        for node, joint in ((n[1], (1, 3, 4, 6, 7, 10, 11, 12)),
                            (n[2], (2, 4, 5, 6, 7, 8, 9, 10, 11, 12)),
                            (n[3], (1, 3)),
                            (n[4], (1, 2, 4, 6, 7, 10, 11, 12)),
                            (n[5], (2, 5, 8, 9, 10, 11, 12)),
                            (n[6], (1, 2, 4, 6)),
                            (n[7], (1, 2, 4, 7, 10, 11, 12)),
                            (n[8], (2, 5, 8, 10, 11, 12)),
                            (n[9], (2, 5, 9)),
                            (n[10], (1, 2, 4, 5, 7, 8, 10, 11, 12)),
                            (n[11], (1, 2, 4, 5, 7, 8, 10, 11)),
                            (n[12], (1, 2, 4, 5, 7, 8, 10, 12))):
            disjoint = allnodes - set(joint)
            for index in joint:
                name = f"Node {index}"
                self.assertIn(name, node.attrs,
                    f"{name} not found in {node.dumps(indent=4)}")
            for index in disjoint:
                name = f"Node {index}"
                self.assertNotIn(name, node.attrs,
                    f"{name} found in {node.dumps(indent=4)}")
