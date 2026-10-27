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

    def test_dfs_stack_mechanics_and_backtracking(self):
        self.graph.load_preset("cyclic")
        res = dfs(self.graph, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["total_pushes"], 1)
        self.assertGreaterEqual(res["total_pops"], 1)
        self.assertGreaterEqual(res["max_structure"], 1)

        # Initial step must be a PUSH of source router R1
        first_step = res["steps"][0]
        self.assertEqual(first_step["operation"], "PUSH")
        self.assertEqual(first_step["current_node"], "R1")
        self.assertEqual(first_step["top"], "R1")
        self.assertEqual(first_step["bottom"], "R1")

        # Second step must be a POP of source router R1
        second_step = res["steps"][1]
        self.assertEqual(second_step["operation"], "POP")
        self.assertEqual(second_step["current_node"], "R1")

        # Backtrack count should be recorded
        self.assertIn("backtrack_count", res)


if __name__ == "__main__":
    unittest.main()
