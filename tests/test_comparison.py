"""
test_comparison.py — Automated Tests for Dual BFS vs. DFS Algorithm Arena.
Verifies simultaneous execution of BFS and DFS on identical topologies,
route differentials, hop comparisons, execution latencies, step counts, and telemetry tables.
"""

import unittest
from network import Graph
import simulation as sim


class TestBFSvsDFSComparison(unittest.TestCase):
    def setUp(self):
        sim.init_session()
        self.graph = Graph()
        self.graph.load_preset("reference")

    def test_comparison_reference_topology(self):
        """Verifies comparison on Reference 7-Node LAN/WAN topology."""
        cmp_data = sim.compare_bfs_and_dfs(self.graph, "N1", "N7")
        self.assertTrue(cmp_data["bfs_res"]["success"])
        self.assertTrue(cmp_data["dfs_res"]["success"])
        self.assertIn("N1", cmp_data["b_path"])
        self.assertIn("N7", cmp_data["b_path"])
        self.assertIn("N1", cmp_data["d_path"])
        self.assertIn("N7", cmp_data["d_path"])

        # Check differentials are calculated
        self.assertIsInstance(cmp_data["hop_delta"], int)
        self.assertIsInstance(cmp_data["cost_delta"], float)
        self.assertIsInstance(cmp_data["time_delta"], float)
        self.assertIsInstance(cmp_data["steps_delta"], int)

        # Check active rendering structures
        self.assertIn("route_nodes", cmp_data["b_active"])
        self.assertIn("route_nodes", cmp_data["d_active"])

        # Check comparison table format
        table = cmp_data["comparison_table"]
        self.assertGreater(len(table), 5)
        metrics = [row["Performance Metric"] for row in table]
        self.assertIn("Discovered Route", metrics)
        self.assertIn("Hop Count", metrics)
        self.assertIn("Total Path Cost / Weight", metrics)
        self.assertIn("Execution Latency", metrics)
        self.assertIn("Total Traversal Steps", metrics)

    def test_comparison_hop_and_path_differentials(self):
        """
        Verifies that on Reference topology, BFS finds a 4-hop route
        while DFS discovers an elongated 6-hop route.
        """
        cmp_data = sim.compare_bfs_and_dfs(self.graph, "N1", "N7")

        self.assertEqual(cmp_data["b_hops"], 4)
        self.assertEqual(cmp_data["d_hops"], 6)
        self.assertEqual(cmp_data["hop_delta"], 2)
        self.assertEqual(cmp_data["b_path"], ["N1", "N2", "N4", "N6", "N7"])
        self.assertEqual(cmp_data["d_path"], ["N1", "N2", "N3", "N5", "N4", "N6", "N7"])
        self.assertIn("BFS Shorter by 2 Hops", cmp_data["route_status"])

    def test_comparison_unreachable_endpoints(self):
        """Verifies comparison handles disconnected/unreachable components gracefully."""
        g_disc = Graph.from_preset("disconnected")
        cmp_data = sim.compare_bfs_and_dfs(g_disc, "A1", "B2")
        self.assertFalse(cmp_data["bfs_res"]["success"])
        self.assertFalse(cmp_data["dfs_res"]["success"])
        self.assertEqual(cmp_data["b_path"], [])
        self.assertEqual(cmp_data["d_path"], [])


if __name__ == "__main__":
    unittest.main()
