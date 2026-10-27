"""
test_failure_lab.py — Automated Tests for Network Failure and Recovery Lab.
Verifies router failure, connection failure, alternate route discovery,
unreachability detection, component restoration, and route comparison analytics.
"""

import unittest
from network import Graph
from algorithms import bfs, dijkstra
from simulation import capture_baseline_route, compare_failure_routes


class TestFailureLab(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.load_preset("reference")

    def test_router_failure_and_alternate_route(self):
        """Verifies router failure triggers alternative detour routing."""
        # Baseline route from N1 to N7 via BFS is N1-N2-N4-N6-N7 (4 hops, cost 19)
        baseline = capture_baseline_route(self.graph, "BFS", "N1", "N7")
        self.assertTrue(baseline["success"])
        self.assertEqual(baseline["path"], ["N1", "N2", "N4", "N6", "N7"])

        # Simulate failure of Router 1 (N2)
        status = self.graph.toggle_router_status("N2")
        self.assertFalse(status)
        self.assertFalse(self.graph.routers["N2"].is_online)

        # Recalculate route
        reroute_res = bfs(self.graph, "N1", "N7")
        self.assertTrue(reroute_res["success"])
        self.assertNotIn("N2", reroute_res["path"])
        # Should detour via N3: N1-N3-N5-N6-N7
        self.assertEqual(reroute_res["path"], ["N1", "N3", "N5", "N6", "N7"])

        # Compare routes
        comparison = compare_failure_routes(baseline, reroute_res)
        self.assertEqual(comparison["status"], "Detour Discovered")
        self.assertEqual(comparison["current_path"], ["N1", "N3", "N5", "N6", "N7"])

    def test_connection_failure_and_alternate_route(self):
        """Verifies individual transmission link failure forces traffic onto a detour."""
        baseline = capture_baseline_route(self.graph, "Dijkstra", "N1", "N7")
        self.assertTrue(baseline["success"])
        self.assertEqual(baseline["path"], ["N1", "N2", "N3", "N5", "N6", "N7"])
        self.assertEqual(baseline["cost"], 17.0)

        # Cut transmission link between N3 and N5
        link_active = self.graph.toggle_connection_status("N3", "N5")
        self.assertFalse(link_active)
        self.assertFalse(self.graph.is_edge_active("N3", "N5"))

        # Recalculate route with Dijkstra
        reroute_res = dijkstra(self.graph, "N1", "N7")
        self.assertTrue(reroute_res["success"])
        # Must avoid cut link N3-N5; routes via N4: N1-N2-N4-N6-N7
        self.assertEqual(reroute_res["path"], ["N1", "N2", "N4", "N6", "N7"])
        self.assertEqual(reroute_res["path_cost"], 19.0)

        comparison = compare_failure_routes(baseline, reroute_res)
        self.assertEqual(comparison["status"], "Detour Discovered")
        self.assertEqual(comparison["detour_cost"], 2.0)

    def test_unreachable_partition_detection(self):
        """Verifies failure of articulation router results in clear unreachable state."""
        baseline = capture_baseline_route(self.graph, "BFS", "N1", "N7")

        # Disable Gateway Switch B (N6) which disconnects N7
        self.graph.toggle_router_status("N6")
        self.assertFalse(self.graph.routers["N6"].is_online)

        reroute_res = bfs(self.graph, "N1", "N7")
        self.assertFalse(reroute_res["success"])
        self.assertEqual(reroute_res["path"], [])

        comparison = compare_failure_routes(baseline, reroute_res)
        self.assertEqual(comparison["status"], "Unreachable / Partitioned")
        self.assertIn("unreachable", comparison["summary"].lower())

    def test_full_restoration_after_recovery(self):
        """Verifies restore_all_failures restores network components and baseline routing."""
        # Fail multiple components
        self.graph.toggle_router_status("N2")
        self.graph.toggle_connection_status("N3", "N5")
        self.assertFalse(self.graph.routers["N2"].is_online)
        self.assertFalse(self.graph.is_edge_active("N3", "N5"))

        # Perform global recovery
        self.graph.restore_all_failures()
        self.assertTrue(self.graph.routers["N2"].is_online)
        self.assertTrue(self.graph.is_edge_active("N3", "N5"))
        self.assertEqual(len(self.graph.failed_edges), 0)

        # Confirm original BFS route is restored
        restored_res = bfs(self.graph, "N1", "N7")
        self.assertTrue(restored_res["success"])
        self.assertEqual(restored_res["path"], ["N1", "N2", "N4", "N6", "N7"])


if __name__ == "__main__":
    unittest.main()
