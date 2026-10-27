"""
Unit tests for network.py (Graph operations, validation, representations, and presets).
"""

import unittest
from network import Graph, validate_router_id


class TestNetworkGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_add_and_remove_router(self):
        self.assertTrue(self.graph.add_router("R1", "Core Router"))
        self.assertIn("R1", self.graph.routers)
        # Duplicate router ID should fail
        self.assertFalse(self.graph.add_router("R1", "Duplicate"))
        # Remove router
        self.assertTrue(self.graph.remove_router("R1"))
        self.assertNotIn("R1", self.graph.routers)
        # Removing non-existent router should fail
        self.assertFalse(self.graph.remove_router("R1"))

    def test_add_and_remove_connection(self):
        self.graph.add_router("R1")
        self.graph.add_router("R2")
        # Self-loop should fail
        self.assertFalse(self.graph.add_connection("R1", "R1"))
        # Valid connection
        self.assertTrue(self.graph.add_connection("R1", "R2"))
        self.assertIn("R2", self.graph.adjacency["R1"])
        self.assertIn("R1", self.graph.adjacency["R2"])
        # Remove connection
        self.assertTrue(self.graph.remove_connection("R1", "R2"))
        self.assertNotIn("R2", self.graph.adjacency["R1"])

    def test_cascading_deletion(self):
        self.graph.add_router("R1")
        self.graph.add_router("R2")
        self.graph.add_router("R3")
        self.graph.add_connection("R1", "R2")
        self.graph.add_connection("R2", "R3")
        # Removing R2 must remove links (R1, R2) and (R2, R3)
        self.graph.remove_router("R2")
        self.assertNotIn("R2", self.graph.routers)
        self.assertNotIn("R2", self.graph.adjacency["R1"])
        self.assertNotIn("R2", self.graph.adjacency["R3"])

    def test_router_status_toggle(self):
        self.graph.add_router("R1", is_online=True)
        self.assertTrue(self.graph.routers["R1"].is_online)
        self.assertFalse(self.graph.toggle_router_status("R1"))
        self.assertFalse(self.graph.routers["R1"].is_online)
        self.assertTrue(self.graph.toggle_router_status("R1"))

    def test_adjacency_list_and_matrix_consistency(self):
        self.graph.load_preset("sample")
        adj_list = self.graph.get_adjacency_list()
        nodes, matrix = self.graph.get_adjacency_matrix()

        self.assertEqual(len(nodes), len(adj_list))
        for i, u in enumerate(nodes):
            for j, v in enumerate(nodes):
                has_edge = v in adj_list[u]
                self.assertEqual(matrix[i][j], 1 if has_edge else 0)

    def test_connected_components(self):
        self.graph.load_preset("disconnected")
        comps = self.graph.get_connected_components()
        self.assertEqual(len(comps), 2)
        self.assertFalse(self.graph.is_connected())

    def test_json_serialization(self):
        self.graph.load_preset("sample")
        data = self.graph.to_dict()
        g2 = Graph()
        success, _ = g2.load_from_dict(data)
        self.assertTrue(success)
        self.assertEqual(len(g2.routers), len(self.graph.routers))
        self.assertEqual(len(g2.get_edges()), len(self.graph.get_edges()))

    def test_rename_router(self):
        self.graph.add_router("R1", "Original Name")
        self.assertTrue(self.graph.rename_router("R1", "New Gateway"))
        self.assertEqual(self.graph.routers["R1"].name, "New Gateway")
        # Empty name should fail
        self.assertFalse(self.graph.rename_router("R1", "   "))
        # Non-existent router should fail
        self.assertFalse(self.graph.rename_router("NONEXISTENT", "Label"))

    def test_duplicate_connection_rejection(self):
        self.graph.add_router("R1")
        self.graph.add_router("R2")
        self.assertTrue(self.graph.add_connection("R1", "R2"))
        # Adding existing link again should return False
        self.assertFalse(self.graph.add_connection("R1", "R2"))
        self.assertFalse(self.graph.add_connection("R2", "R1"))

    def test_reachability(self):
        self.graph.load_preset("direct")  # R1 - R2 - R3 - R4
        self.assertTrue(self.graph.is_reachable("R1", "R4"))
        # Set intermediate R2 offline
        self.graph.routers["R2"].is_online = False
        self.assertFalse(self.graph.is_reachable("R1", "R4"))

    def test_graph_summary(self):
        self.graph.load_preset("sample")
        summary = self.graph.get_summary()
        self.assertEqual(summary["total_routers"], len(self.graph.routers))
        self.assertEqual(summary["online_routers"], len(self.graph.routers))
        self.assertEqual(summary["total_edges"], len(self.graph.get_edges()))
        self.assertTrue(summary["is_connected"])

    def test_router_id_validation(self):
        ok, _ = validate_router_id("R1")
        self.assertTrue(ok)
        ok, _ = validate_router_id("")
        self.assertFalse(ok)
        ok, _ = validate_router_id("TOOLONGID123")
        self.assertFalse(ok)
        ok, _ = validate_router_id("R-1!")
        self.assertFalse(ok)

    def test_reference_preset_and_edge_weights(self):
        self.graph.load_preset("reference")
        self.assertEqual(len(self.graph.routers), 7)
        self.assertIn("N1", self.graph.routers)
        self.assertIn("N7", self.graph.routers)
        self.assertEqual(self.graph.get_weight("N1", "N2"), 4.0)
        self.assertEqual(self.graph.get_weight("N6", "N7"), 1.0)
        self.assertTrue(self.graph.is_connected())


if __name__ == "__main__":
    unittest.main()
