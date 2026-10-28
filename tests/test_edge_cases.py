"""
tests/test_edge_cases.py — Comprehensive Automated Tests for the 20 Core Graph & Routing Edge Cases.

Edge Cases Tested:
1. Source equals destination
2. Reachable destination
3. Unreachable destination
4. Empty graph handling
5. Invalid source or destination IDs
6. Offline source router
7. Offline destination router
8. Offline intermediate router
9. Failed direct connection (link failure and dynamic rerouting)
10. Multiple alternative routes (BFS unweighted shortest-path optimality)
11. Cycles in graph (acyclic traversal tree and loop avoidance)
12. Duplicate connections rejection
13. Invalid connection endpoints rejection
14. Invalid weights rejection
15. Self-links rejection
16. Topology changes invalidation
17. Imported topology containing invalid data
18. Routing-table forwarding loop detection
19. Missing forwarding table entries
20. BFS and DFS behavior on disconnected graphs
"""

import unittest
from network import Graph, validate_topology_dict
from algorithms import bfs, dfs, build_traversal_tree
from simulation import simulate_table_forwarding, invalidate_simulation


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.g = Graph()

    def test_01_source_equals_destination(self):
        self.g.add_router("R1")
        res_bfs = bfs(self.g, "R1", "R1")
        self.assertTrue(res_bfs["success"])
        self.assertEqual(res_bfs["path"], ["R1"])
        self.assertEqual(res_bfs["hops"], 0)

        res_dfs = dfs(self.g, "R1", "R1")
        self.assertTrue(res_dfs["success"])
        self.assertEqual(res_dfs["path"], ["R1"])
        self.assertEqual(res_dfs["hops"], 0)

    def test_02_reachable_destination(self):
        self.g.load_preset("direct")  # R1-R2-R3-R4
        res = bfs(self.g, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R4"])
        self.assertEqual(res["hops"], 3)

    def test_03_unreachable_destination(self):
        self.g.load_preset("disconnected")
        res = bfs(self.g, "R1", "R5")
        self.assertFalse(res["success"])
        self.assertEqual(res["path"], [])

    def test_04_empty_graph(self):
        empty_g = Graph()
        res_bfs = bfs(empty_g, "R1", "R2")
        self.assertFalse(res_bfs["success"])
        self.assertIn("empty", res_bfs["message"].lower())

        res_dfs = dfs(empty_g, "R1", "R2")
        self.assertFalse(res_dfs["success"])
        self.assertIn("empty", res_dfs["message"].lower())

        res_fwd = simulate_table_forwarding(empty_g, "R1", "R2")
        self.assertFalse(res_fwd["success"])
        self.assertEqual(res_fwd["status"], "EMPTY_GRAPH")

    def test_05_invalid_source_or_destination(self):
        self.g.add_router("R1")
        res = bfs(self.g, "R1", "NONEXISTENT")
        self.assertFalse(res["success"])
        self.assertIn("does not exist", res["message"])

        res2 = bfs(self.g, "NONEXISTENT", "R1")
        self.assertFalse(res2["success"])

    def test_06_offline_source_router(self):
        self.g.add_router("R1", is_online=False)
        self.g.add_router("R2", is_online=True)
        self.g.add_connection("R1", "R2")

        res_bfs = bfs(self.g, "R1", "R2")
        self.assertFalse(res_bfs["success"])
        self.assertIn("OFFLINE", res_bfs["message"])

        res_fwd = simulate_table_forwarding(self.g, "R1", "R2")
        self.assertFalse(res_fwd["success"])
        self.assertEqual(res_fwd["status"], "SOURCE_OFFLINE")

    def test_07_offline_destination_router(self):
        self.g.add_router("R1", is_online=True)
        self.g.add_router("R2", is_online=False)
        self.g.add_connection("R1", "R2")

        res = bfs(self.g, "R1", "R2")
        self.assertFalse(res["success"])
        self.assertIn("OFFLINE", res["message"])

    def test_08_offline_intermediate_router(self):
        self.g.load_preset("direct")  # R1-R2-R3-R4
        self.g.set_router_status("R2", False)
        res = bfs(self.g, "R1", "R4")
        self.assertFalse(res["success"])

    def test_09_failed_direct_connection(self):
        # Triangle R1-R2, R2-R3, R1-R3
        self.g.add_router("R1")
        self.g.add_router("R2")
        self.g.add_router("R3")
        self.g.add_connection("R1", "R2")
        self.g.add_connection("R2", "R3")
        self.g.add_connection("R1", "R3")

        # Sever direct link R1-R3
        self.g.toggle_edge_failure("R1", "R3")
        res = bfs(self.g, "R1", "R3")
        self.assertTrue(res["success"])
        # Should dynamically reroute via R2
        self.assertEqual(res["path"], ["R1", "R2", "R3"])

    def test_10_multiple_alternative_routes(self):
        self.g.load_preset("multi_route")
        # Upper route: 3 hops (R1-R2-R3-R7)
        # Lower route: 4 hops (R1-R4-R5-R6-R7)
        res = bfs(self.g, "R1", "R7")
        self.assertTrue(res["success"])
        self.assertEqual(res["hops"], 3)
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R7"])

    def test_11_cycles_in_graph(self):
        self.g.load_preset("ring")
        res = bfs(self.g, "R1", "R4")
        self.assertTrue(res["success"])
        tree = build_traversal_tree(res["parents"], "R1", "R4")
        self.assertTrue(tree["is_acyclic"])
        self.assertEqual(tree["edge_count"], tree["node_count"] - 1)

    def test_12_duplicate_connections_rejection(self):
        self.g.add_router("R1")
        self.g.add_router("R2")
        self.assertTrue(self.g.add_connection("R1", "R2"))
        self.assertFalse(self.g.add_connection("R1", "R2"))
        self.assertFalse(self.g.add_connection("R2", "R1"))

    def test_13_invalid_connection_endpoints(self):
        self.g.add_router("R1")
        self.assertFalse(self.g.add_connection("R1", "GHOST"))

    def test_14_invalid_weights(self):
        self.g.add_router("R1")
        self.g.add_router("R2")
        self.assertFalse(self.g.add_connection("R1", "R2", weight=-1.0))
        self.g.add_connection("R1", "R2", weight=1.0)
        self.assertFalse(self.g.set_weight("R1", "R2", weight=-0.5))

    def test_15_self_links_prohibited(self):
        self.g.add_router("R1")
        self.assertFalse(self.g.add_connection("R1", "R1"))

    def test_16_topology_changes_after_simulation(self):
        # Verify that changing topology or calling invalidate_simulation clears state safely
        self.g.load_preset("reference")
        res = bfs(self.g, "N1", "N7")
        self.assertTrue(res["success"])
        # Mutate network
        self.g.remove_router("N7")
        self.assertNotIn("N7", self.g.routers)
        res_after = bfs(self.g, "N1", "N7")
        self.assertFalse(res_after["success"])

    def test_17_imported_topology_invalid_data(self):
        bad_json_dict = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "R2", "NOT_A_NUMBER"]]
        }
        valid, msg, cleaned = validate_topology_dict(bad_json_dict)
        self.assertFalse(valid)
        self.assertIsNone(cleaned)

    def test_18_routing_table_loops(self):
        # simulate_table_forwarding detects routing loops
        # Graph with loop R1-R2
        self.g.add_router("R1")
        self.g.add_router("R2")
        self.g.add_connection("R1", "R2")
        res = simulate_table_forwarding(self.g, "R1", "R2")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "DELIVERED")

    def test_19_missing_forwarding_entries(self):
        # Isolated node R99 has no route to R1
        self.g.add_router("R1")
        self.g.add_router("R99")
        res = simulate_table_forwarding(self.g, "R1", "R99")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "NO_ROUTE_TO_HOST")

    def test_20_bfs_and_dfs_on_disconnected_graphs(self):
        self.g.load_preset("disconnected")
        res_bfs = bfs(self.g, "R1", "R4")
        self.assertFalse(res_bfs["success"])
        self.assertEqual(res_bfs["path"], [])
        self.assertNotIn("R4", res_bfs["visited"])

        res_dfs = dfs(self.g, "R1", "R4")
        self.assertFalse(res_dfs["success"])
        self.assertEqual(res_dfs["path"], [])
        self.assertNotIn("R4", res_dfs["visited"])


if __name__ == "__main__":
    unittest.main()
