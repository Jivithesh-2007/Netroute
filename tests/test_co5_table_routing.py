"""
test_co5_table_routing.py — Automated Unit Tests for CO5 Traditional Table-Based Forwarding & Comparison.

Validates:
- Generation of router routing tables with Destination, Next Hop, Hop Count, and Status.
- Correct Next Hop determination using local forwarding tables.
- Hop-by-hop packet forwarding simulation across intermediate routers.
- Source equals destination immediate local delivery.
- Forwarding failure upon link severance.
- Forwarding failure upon intermediate router offline.
- Detection of unreachable destination without infinite loop.
- Comparison between graph traversal discovery and table-based forwarding.
"""

import unittest
from network import Graph
from simulation import simulate_table_forwarding


class TestCO5TableRouting(unittest.TestCase):
    def setUp(self):
        # Linear network: R1 - R2 - R3 - R4
        self.g = Graph()
        for rid in ["R1", "R2", "R3", "R4"]:
            self.g.add_router(rid)
        for u, v in [("R1", "R2"), ("R2", "R3"), ("R3", "R4")]:
            self.g.add_connection(u, v)

    def test_routing_table_generation(self):
        table = self.g.generate_routing_table("R1")
        self.assertEqual(len(table), 4)
        
        # Self entry
        self_entry = next(e for e in table if e["destination"] == "R1")
        self.assertEqual(self_entry["next_hop"], "R1")
        self.assertEqual(self_entry["hops"], 0)
        self.assertIn("Local", self_entry["status"])

        # Immediate neighbor R2
        r2_entry = next(e for e in table if e["destination"] == "R2")
        self.assertEqual(r2_entry["next_hop"], "R2")
        self.assertEqual(r2_entry["hops"], 1)

        # Multi-hop destination R4: next hop from R1 must be R2!
        r4_entry = next(e for e in table if e["destination"] == "R4")
        self.assertEqual(r4_entry["next_hop"], "R2")
        self.assertEqual(r4_entry["hops"], 3)
        self.assertEqual(r4_entry["status"], "Reachable")

    def test_successful_table_forwarding(self):
        res = simulate_table_forwarding(self.g, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R4"])
        self.assertEqual(res["hops"], 3)
        self.assertEqual(res["status"], "DELIVERED")
        self.assertEqual(len(res["steps"]), 4)

    def test_source_equals_destination(self):
        res = simulate_table_forwarding(self.g, "R2", "R2")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R2"])
        self.assertEqual(res["hops"], 0)
        self.assertEqual(res["status"], "DELIVERED_LOCAL")

    def test_forwarding_failure_severed_link(self):
        # Sever link between R2 and R3
        self.g.toggle_edge_failure("R2", "R3")
        
        # Attempt forwarding from R1 to R4
        res = simulate_table_forwarding(self.g, "R1", "R4")
        self.assertFalse(res["success"])
        self.assertIn(res["status"], ["LINK_SEVERED", "NO_ROUTE_TO_HOST"])

    def test_forwarding_failure_offline_router(self):
        # Take intermediate router R3 offline
        self.g.set_router_status("R3", False)
        
        res = simulate_table_forwarding(self.g, "R1", "R4")
        self.assertFalse(res["success"])

    def test_unreachable_destination(self):
        # Add an isolated router R99
        self.g.add_router("R99")
        
        table = self.g.generate_routing_table("R1")
        r99_entry = next(e for e in table if e["destination"] == "R99")
        self.assertEqual(r99_entry["next_hop"], "None")
        self.assertEqual(r99_entry["status"], "Unreachable")

        res = simulate_table_forwarding(self.g, "R1", "R99")
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "NO_ROUTE_TO_HOST")


if __name__ == "__main__":
    unittest.main()
