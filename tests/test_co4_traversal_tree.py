"""
test_co4_traversal_tree.py — Automated Unit Tests for CO4 Tree Structures.

Validates:
- Correct BFS tree root.
- Correct parent-child relationships.
- No duplicate tree nodes.
- No cycles in the traversal tree (strictly acyclic).
- Unreachable vertices excluded from the tree.
- Correct source-to-destination path reconstruction.
- Tree invariant: E = V - 1 for reachable vertices.
"""

import unittest
from network import Graph
from algorithms import bfs, build_traversal_tree


class TestCO4TraversalTree(unittest.TestCase):
    def setUp(self):
        # Create a cyclic network: R1 - R2 - R3 - R4 - R1 (a 4-node loop) plus R5
        self.cyclic_graph = Graph()
        for rid in ["R1", "R2", "R3", "R4", "R5"]:
            self.cyclic_graph.add_router(rid)
        for u, v in [("R1", "R2"), ("R2", "R3"), ("R3", "R4"), ("R4", "R1"), ("R3", "R5")]:
            self.cyclic_graph.add_connection(u, v)

    def test_single_root_and_invariants(self):
        bfs_res = bfs(self.cyclic_graph, "R1", "R5")
        self.assertTrue(bfs_res["success"])
        
        tree = build_traversal_tree(bfs_res["parents"], "R1", "R5")
        
        # Invariant 1: Exactly one root
        self.assertEqual(tree["root"], "R1")
        self.assertEqual(tree["levels"]["R1"], 0)
        
        # Invariant 2: Total vertices = 5, total edges = 4 (E = V - 1)
        self.assertEqual(tree["node_count"], 5)
        self.assertEqual(tree["edge_count"], 4)
        
        # Invariant 3: No duplicate nodes
        self.assertEqual(len(tree["nodes"]), len(set(tree["nodes"])))

    def test_acyclic_property_on_cyclic_network(self):
        # Even though the network graph has a 4-node cycle, the traversal tree must be strictly acyclic
        bfs_res = bfs(self.cyclic_graph, "R1", "R5")
        tree = build_traversal_tree(bfs_res["parents"], "R1", "R5")
        
        self.assertTrue(tree["is_acyclic"])
        # In a tree with 5 nodes and 4 edges, every node except root has exactly one parent
        for child, parent in bfs_res["parents"].items():
            if child != "R1":
                self.assertIsNotNone(parent)
                # Parent must be at a lower depth level
                self.assertEqual(tree["levels"][child], tree["levels"][parent] + 1)

    def test_unreachable_node_exclusion(self):
        # Add an isolated router R99
        self.cyclic_graph.add_router("R99")
        bfs_res = bfs(self.cyclic_graph, "R1", "R99")
        self.assertFalse(bfs_res["success"])
        
        tree = build_traversal_tree(bfs_res["parents"], "R1", "R99")
        # R99 must NOT be in the traversal tree
        self.assertNotIn("R99", tree["nodes"])
        self.assertNotIn("R99", tree["levels"])
        self.assertFalse(tree["reachable"])

    def test_path_reconstruction_along_tree(self):
        bfs_res = bfs(self.cyclic_graph, "R1", "R5")
        tree = build_traversal_tree(bfs_res["parents"], "R1", "R5")
        
        self.assertEqual(tree["path_to_dest"], bfs_res["path"])
        self.assertEqual(tree["path_to_dest"][0], "R1")
        self.assertEqual(tree["path_to_dest"][-1], "R5")

    def test_empty_parents_handling(self):
        tree = build_traversal_tree({}, "R1", "R2")
        self.assertEqual(tree["node_count"], 0)
        self.assertEqual(tree["edge_count"], 0)
        self.assertTrue(tree["is_acyclic"])


if __name__ == "__main__":
    unittest.main()
