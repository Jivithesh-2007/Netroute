"""
test_dijkstra.py — Comprehensive Unit Tests for Dijkstra's Shortest Path Algorithm.
Verifies minimum-total-cost routing, priority queue state recording, non-negative weight checks,
differentiation from BFS minimum-hop routing, and edge failure avoidance.
"""

import unittest
from network import Graph
from algorithms import dijkstra, bfs


class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.load_preset("reference")

    def test_dijkstra_minimum_cost_route(self):
        """Verifies Dijkstra discovers the minimum-cost path from N1 to N7."""
        res = dijkstra(self.graph, "N1", "N7")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["N1", "N2", "N3", "N5", "N6", "N7"])
        self.assertEqual(res["path_cost"], 17.0)
        self.assertEqual(res["hops"], 5)

    def test_dijkstra_differs_from_bfs_min_hop(self):
        """
        Verifies the fundamental DSA distinction:
        BFS finds the minimum-hop route, while Dijkstra finds the minimum-total-cost route.
        """
        diff_graph = Graph()
        diff_graph.load_preset("weighted_diff")

        bfs_res = bfs(diff_graph, "S", "D")
        dijk_res = dijkstra(diff_graph, "S", "D")

        self.assertTrue(bfs_res["success"])
        self.assertTrue(dijk_res["success"])

        # BFS optimizes hops: S -> A -> D (2 hops, cost: 1 + 12 = 13)
        self.assertEqual(bfs_res["path"], ["S", "A", "D"])
        self.assertEqual(bfs_res["hops"], 2)
        self.assertEqual(bfs_res["path_cost"], 13.0)

        # Dijkstra optimizes total weight: S -> A -> B -> D (3 hops, cost: 1 + 1 + 2 = 4)
        self.assertEqual(dijk_res["path"], ["S", "A", "B", "D"])
        self.assertEqual(dijk_res["hops"], 3)
        self.assertEqual(dijk_res["path_cost"], 4.0)

        # Confirm the algorithmic distinction mathematically
        self.assertLess(bfs_res["hops"], dijk_res["hops"])
        self.assertLess(dijk_res["path_cost"], bfs_res["path_cost"])

    def test_dijkstra_zero_weight_edge(self):
        """Verifies that Dijkstra supports zero-weight links without infinite loops."""
        g = Graph()
        g.add_router("A", x=100, y=100)
        g.add_router("B", x=200, y=100)
        g.add_router("C", x=300, y=100)
        g.add_connection("A", "B", weight=0.0)
        g.add_connection("B", "C", weight=5.0)

        res = dijkstra(g, "A", "C")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["A", "B", "C"])
        self.assertEqual(res["path_cost"], 5.0)

    def test_dijkstra_negative_weight_rejection(self):
        """Verifies Dijkstra strictly rejects networks with negative edge weights."""
        g = Graph()
        g.add_router("A", x=100, y=100)
        g.add_router("B", x=200, y=100)
        g.add_connection("A", "B", weight=2.0)
        # Directly insert negative weight for testing validation
        g.weights[tuple(sorted(("A", "B")))] = -3.0

        res = dijkstra(g, "A", "B")
        self.assertFalse(res["success"])
        self.assertIn("non-negative", res["message"].lower())

    def test_dijkstra_source_equals_destination(self):
        """Verifies 0 hops and 0 cost when source is identical to destination."""
        res = dijkstra(self.graph, "N2", "N2")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["N2"])
        self.assertEqual(res["hops"], 0)
        self.assertEqual(res["path_cost"], 0.0)

    def test_dijkstra_unreachable_destination(self):
        """Verifies Dijkstra returns success=False for disconnected destinations."""
        g = Graph()
        g.load_preset("disconnected")
        res = dijkstra(g, "R1", "R4")
        self.assertFalse(res["success"])
        self.assertEqual(res["path"], [])
        self.assertEqual(res["hops"], 0)

    def test_dijkstra_cyclic_graph(self):
        """Verifies Dijkstra terminates correctly and finds shortest cost on cyclic meshes."""
        g = Graph()
        g.load_preset("cyclic")
        res = dijkstra(g, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertTrue(len(res["path"]) >= 2)

    def test_dijkstra_offline_router_avoidance(self):
        """Verifies Dijkstra routes around offline hardware."""
        # N2 is on the shortest cost path: N1 -> N2 -> N3 -> N5 -> N6 -> N7 (cost: 17)
        self.graph.toggle_router_status("N2")
        self.assertFalse(self.graph.routers["N2"].is_online)

        res = dijkstra(self.graph, "N1", "N7")
        self.assertTrue(res["success"])
        self.assertNotIn("N2", res["path"])
        # Should take N1 -> N3 -> N5 -> N6 -> N7 (cost: 8 + 2 + 7 + 1 = 18)
        self.assertEqual(res["path"], ["N1", "N3", "N5", "N6", "N7"])
        self.assertEqual(res["path_cost"], 18.0)

    def test_dijkstra_failed_link_avoidance(self):
        """Verifies Dijkstra routes around failed/disabled links."""
        # Disable link N3 <-> N5 (weight: 2)
        self.graph.toggle_connection_status("N3", "N5")
        self.assertFalse(self.graph.is_edge_active("N3", "N5"))

        res = dijkstra(self.graph, "N1", "N7")
        self.assertTrue(res["success"])
        self.assertNotIn(("N3", "N5"), [tuple(sorted((res["path"][i], res["path"][i+1]))) for i in range(len(res["path"]) - 1)])
        # Must detour via N2 -> N4 -> N6 (cost: 4 + 10 + 4 + 1 = 19)
        self.assertEqual(res["path"], ["N1", "N2", "N4", "N6", "N7"])
        self.assertEqual(res["path_cost"], 19.0)

    def test_dijkstra_step_log_and_queue(self):
        """Verifies step records include priority queue, tentative distances, and operations."""
        res = dijkstra(self.graph, "N1", "N7")
        self.assertGreater(len(res["steps"]), 0)
        first_step = res["steps"][0]
        self.assertEqual(first_step["operation"], "INIT")
        self.assertIn("priority_queue", first_step)
        self.assertIn("tentative_distances", first_step)

        # Check that EXTRACT_MIN and RELAX_EDGE operations were captured
        ops = [s["operation"] for s in res["steps"]]
        self.assertIn("EXTRACT_MIN", ops)
        self.assertIn("RELAX_EDGE", ops)
        self.assertIn("COMPLETE", ops)


if __name__ == "__main__":
    unittest.main()
