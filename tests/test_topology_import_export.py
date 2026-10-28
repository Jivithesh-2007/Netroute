"""
tests/test_topology_import_export.py — Unit Tests for Topology JSON Import/Export & Schema Validation.

Validates:
- Graph export to compliant JSON.
- Clean round-trip import/export preserving coordinates, weights, and status flags.
- Rejection of malformed JSON strings.
- Rejection of duplicate router IDs.
- Rejection of self-loops.
- Rejection of duplicate connections.
- Rejection of undefined endpoint references.
- Rejection of invalid (negative or non-finite) weights.
- Candidate graph isolation (guaranteeing active graph is never partially mutated on error).
"""

import unittest
import json
from network import Graph, validate_topology_dict, export_topology_json, import_topology_json


class TestTopologyImportExport(unittest.TestCase):
    def setUp(self):
        self.g = Graph(name="Test Topology")
        self.g.add_router("N1", name="Node 1", x=100.0, y=150.0, is_online=True)
        self.g.add_router("N2", name="Node 2", x=250.0, y=150.0, is_online=True)
        self.g.add_router("N3", name="Node 3", x=400.0, y=200.0, is_online=False)
        self.g.add_connection("N1", "N2", weight=3.5)
        self.g.add_connection("N2", "N3", weight=2.0)
        self.g.toggle_edge_failure("N1", "N2")

    def test_export_structure(self):
        json_str = export_topology_json(self.g, name="Exported Net")
        data = json.loads(json_str)

        self.assertEqual(data["name"], "Exported Net")
        self.assertFalse(data["directed"])
        self.assertEqual(len(data["routers"]), 3)
        self.assertEqual(len(data["edges"]), 2)
        self.assertEqual(len(data["failed_edges"]), 1)

    def test_round_trip_integrity(self):
        json_str = export_topology_json(self.g)
        ok, msg, imported_g = import_topology_json(json_str)

        self.assertTrue(ok)
        self.assertIsNotNone(imported_g)
        self.assertEqual(len(imported_g.routers), len(self.g.routers))
        self.assertEqual(len(imported_g.get_edges()), len(self.g.get_edges()))

        # Check routers and coordinates
        for rid, router in self.g.routers.items():
            self.assertIn(rid, imported_g.routers)
            imp_r = imported_g.routers[rid]
            self.assertEqual(imp_r.name, router.name)
            self.assertEqual(imp_r.x, router.x)
            self.assertEqual(imp_r.y, router.y)
            self.assertEqual(imp_r.is_online, router.is_online)

        # Check connection weights and failed status
        self.assertEqual(imported_g.get_weight("N1", "N2"), 3.5)
        self.assertEqual(imported_g.get_weight("N2", "N3"), 2.0)
        self.assertFalse(imported_g.is_edge_active("N1", "N2"))
        self.assertTrue(imported_g.is_edge_active("N2", "N3"))

    def test_reject_duplicate_router_ids(self):
        bad_data = {
            "routers": [
                {"id": "R1", "x": 100, "y": 100},
                {"id": "R1", "x": 200, "y": 200}
            ],
            "edges": []
        }
        valid, msg, cleaned = validate_topology_dict(bad_data)
        self.assertFalse(valid)
        self.assertIn("Duplicate router ID", msg)

    def test_reject_self_loops(self):
        bad_data = {
            "routers": [{"id": "R1"}],
            "edges": [["R1", "R1", 1.0]]
        }
        valid, msg, cleaned = validate_topology_dict(bad_data)
        self.assertFalse(valid)
        self.assertIn("self-link", msg.lower())

    def test_reject_undefined_endpoints(self):
        bad_data = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "UNKNOWN", 1.0]]
        }
        valid, msg, cleaned = validate_topology_dict(bad_data)
        self.assertFalse(valid)
        self.assertIn("undefined router ID", msg)

    def test_reject_negative_weight(self):
        bad_data = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "R2", -5.0]]
        }
        valid, msg, cleaned = validate_topology_dict(bad_data)
        self.assertFalse(valid)
        self.assertIn("non-negative", msg)

    def test_reject_duplicate_connections(self):
        bad_data = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "R2", 1.0], ["R2", "R1", 2.0]]
        }
        valid, msg, cleaned = validate_topology_dict(bad_data)
        self.assertFalse(valid)
        self.assertIn("Duplicate connection", msg)

    def test_reject_invalid_json_syntax(self):
        ok, msg, candidate = import_topology_json("{this is not valid json")
        self.assertFalse(ok)
        self.assertIsNone(candidate)
        self.assertIn("Invalid JSON syntax", msg)

    def test_candidate_graph_isolation(self):
        # Ensure active graph is not corrupted when load_from_dict receives invalid data
        orig_router_count = len(self.g.routers)
        orig_edge_count = len(self.g.get_edges())

        ok, msg = self.g.load_from_dict({"routers": [{"id": "R1"}, {"id": "R1"}], "edges": []})
        self.assertFalse(ok)
        self.assertEqual(len(self.g.routers), orig_router_count)
        self.assertEqual(len(self.g.get_edges()), orig_edge_count)


if __name__ == "__main__":
    unittest.main()
