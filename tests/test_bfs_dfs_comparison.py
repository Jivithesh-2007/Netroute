"""
test_bfs_dfs_comparison.py — Unit tests for BFS vs. DFS Comparative Evaluation Engine.
"""

import unittest
from network import Graph
from algorithms import compare_bfs_dfs, bfs, dfs


class TestBFSDFSComparison(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_comparison_structure_and_keys(self):
        """Verifies that compare_bfs_dfs returns all required comparative metrics and guide sections."""
        self.graph.load_preset("reference")
        res = compare_bfs_dfs(self.graph, "N1", "N7")

        self.assertIn("source", res)
        self.assertIn("destination", res)
        self.assertIn("both_success", res)
        self.assertIn("bfs", res)
        self.assertIn("dfs", res)
        self.assertIn("bfs_hops", res)
        self.assertIn("dfs_hops", res)
        self.assertIn("hop_delta", res)
        self.assertIn("verdict_title", res)
        self.assertIn("verdict_badge", res)
        self.assertIn("verdict_summary", res)
        self.assertIn("suggestions", res)
        self.assertIn("scenario_guide", res)

        self.assertTrue(len(res["suggestions"]) >= 4)
        self.assertTrue(len(res["scenario_guide"]) >= 5)

    def test_multi_route_optimality_delta(self):
        """Verifies that BFS finds the strictly shortest route on multi-route topologies."""
        self.graph.load_preset("multi_route")
        # Upper route: R1 - R2 - R3 - R7 (3 hops)
        # Lower route: R1 - R4 - R5 - R6 - R7 (4 hops)
        res = compare_bfs_dfs(self.graph, "R1", "R7")

        self.assertTrue(res["both_success"])
        self.assertEqual(res["bfs_hops"], 3)
        self.assertGreaterEqual(res["dfs_hops"], 3)
        self.assertGreaterEqual(res["hop_delta"], 0)
        self.assertIn("BFS", res["winner"])

    def test_direct_topology_convergence(self):
        """On a simple linear graph, BFS and DFS converge on the same path."""
        self.graph.load_preset("direct")
        res = compare_bfs_dfs(self.graph, "R1", "R4")

        self.assertTrue(res["both_success"])
        self.assertTrue(res["same_path"])
        self.assertEqual(res["bfs_hops"], 3)
        self.assertEqual(res["dfs_hops"], 3)
        self.assertEqual(res["hop_delta"], 0)

    def test_disconnected_graph_unreachable(self):
        """When nodes are disconnected, both report failure and mutual consistency."""
        self.graph.load_preset("disconnected")
        res = compare_bfs_dfs(self.graph, "R1", "R6")

        self.assertFalse(res["both_success"])
        self.assertFalse(res["bfs"]["success"])
        self.assertFalse(res["dfs"]["success"])
        self.assertIn("Unreachable", res["verdict_title"])

    def test_offline_router_avoidance_comparison(self):
        """Verifies comparison respects offline nodes."""
        self.graph.load_preset("offline_router")
        # R2 is offline on bridge (R1-R2-R3). Bypass is R1-R4-R3-R5.
        res = compare_bfs_dfs(self.graph, "R1", "R5")

        self.assertTrue(res["both_success"])
        self.assertNotIn("R2", res["bfs"]["path"])
        self.assertNotIn("R2", res["dfs"]["path"])


if __name__ == "__main__":
    unittest.main()
