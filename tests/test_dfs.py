"""
Unit tests for DFS algorithm implementation (deep exploration, stack mechanics, backtracking).
"""

import unittest
from network import Graph
from algorithms import dfs


class TestDFS(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_dfs_reachable_path(self):
        self.graph.load_preset("direct")
        res = dfs(self.graph, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R4"])

    def test_dfs_source_equals_dest(self):
        self.graph.load_preset("sample")
        res = dfs(self.graph, "R1", "R1")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1"])
        self.assertEqual(res["hops"], 0)

    def test_dfs_cyclic_loop_prevention(self):
        self.graph.load_preset("cyclic")
        res = dfs(self.graph, "R1", "R4")
        self.assertTrue(res["success"])
        # Visited path must have no duplicate vertices (cycles avoided)
        self.assertEqual(len(res["path"]), len(set(res["path"])))

    def test_dfs_unreachable_destination(self):
        self.graph.load_preset("disconnected")
        res = dfs(self.graph, "R1", "R6")
        self.assertFalse(res["success"])
        self.assertEqual(res["path"], [])

    def test_dfs_offline_router_avoidance(self):
        self.graph.load_preset("offline_router")
        # R2 is offline
        res = dfs(self.graph, "R1", "R5")
        self.assertTrue(res["success"])
        self.assertNotIn("R2", res["path"])


if __name__ == "__main__":
    unittest.main()
