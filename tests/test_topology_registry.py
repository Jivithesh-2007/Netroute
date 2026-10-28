"""
tests/test_topology_registry.py — Automated Unit Tests for Data-Driven Topology Registry.

Validates:
- Discovery of JSON topologies in data directory.
- Availability of required educational presets.
- Extraction of metadata (names, router/edge counts).
- Loading topologies into Graph instances.
- Graceful handling of non-existent or malformed presets.
- Preset fallback behavior.
"""

import unittest
import os
import tempfile
import json
from topology_registry import TopologyRegistry, get_topology_registry
from network import Graph


class TestTopologyRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = get_topology_registry()

    def test_default_presets_discovered(self):
        presets = self.registry.get_available_presets()
        self.assertGreaterEqual(len(presets), 5)
        self.assertIn("reference", presets)
        self.assertIn("mesh", presets)
        self.assertIn("ring", presets)
        self.assertIn("disconnected", presets)

    def test_preset_metadata(self):
        ref = self.registry.get_available_presets()["reference"]
        self.assertEqual(ref["id"], "reference")
        self.assertEqual(ref["router_count"], 7)
        self.assertEqual(ref["edge_count"], 9)
        self.assertIn("Reference", ref["name"])

    def test_load_graph_from_preset(self):
        g = self.registry.load_graph("reference")
        self.assertIsInstance(g, Graph)
        self.assertEqual(len(g.routers), 7)
        self.assertEqual(len(g.get_edges()), 9)
        self.assertIn("N1", g.routers)
        self.assertIn("N7", g.routers)

    def test_fallback_on_unknown_preset(self):
        # Should gracefully return reference graph or first available rather than None/crash
        g = self.registry.load_graph("completely_nonexistent_preset_key")
        self.assertIsInstance(g, Graph)
        self.assertGreater(len(g.routers), 0)

    def test_custom_data_dir_and_malformed_tolerance(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Valid file
            valid_net = {
                "name": "Temp Test Net",
                "routers": [{"id": "A1"}, {"id": "A2"}],
                "edges": [["A1", "A2", 1.5]]
            }
            with open(os.path.join(tmpdir, "test_network.json"), "w", encoding="utf-8") as f:
                json.dump(valid_net, f)

            # 2. Corrupt/malformed JSON file
            with open(os.path.join(tmpdir, "corrupt.json"), "w", encoding="utf-8") as f:
                f.write("corrupted content { [")

            # 3. Invalid schema file (duplicate ID)
            invalid_schema = {
                "routers": [{"id": "B1"}, {"id": "B1"}],
                "edges": []
            }
            with open(os.path.join(tmpdir, "invalid.json"), "w", encoding="utf-8") as f:
                json.dump(invalid_schema, f)

            reg = TopologyRegistry(data_dir=tmpdir)
            presets = reg.get_available_presets()

            # Corrupt and invalid files should be skipped without raising exceptions
            self.assertEqual(len(presets), 1)
            self.assertIn("test_network", presets)
            loaded = reg.load_graph("test_network")
            self.assertIsNotNone(loaded)
            self.assertEqual(len(loaded.routers), 2)


if __name__ == "__main__":
    unittest.main()
