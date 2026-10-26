"""
Unit tests for BFS algorithm implementation (shortest hops, queue mechanics, edge cases).
"""

import unittest
from network import Graph
from algorithms import bfs


class TestBFS(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_direct_route(self):
        self.graph.load_preset("direct")
        res = bfs(self.graph, "R1", "R4")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R4"])
        self.assertEqual(res["hops"], 3)

    def test_shortest_hop_guarantee_on_multiple_routes(self):
        self.graph.load_preset("multi_route")
        # Upper route: R1 - R2 - R3 - R7 (3 hops)
        # Lower route: R1 - R4 - R5 - R6 - R7 (4 hops)
        res = bfs(self.graph, "R1", "R7")
        self.assertTrue(res["success"])
        self.assertEqual(res["hops"], 3)
        self.assertEqual(res["path"], ["R1", "R2", "R3", "R7"])

    def test_source_equals_destination(self):
        self.graph.load_preset("sample")
        res = bfs(self.graph, "R1", "R1")
        self.assertTrue(res["success"])
        self.assertEqual(res["path"], ["R1"])
        self.assertEqual(res["hops"], 0)

    def test_unreachable_destination(self):
        self.graph.load_preset("disconnected")
        res = bfs(self.graph, "R1", "R6")
        self.assertFalse(res["success"])
        self.assertEqual(res["path"], [])

    def test_offline_router_avoidance(self):
        self.graph.load_preset("offline_router")
        # R2 is offline on bridge (R1-R2-R3). Bypass is R1-R4-R3-R5.
        res = bfs(self.graph, "R1", "R5")
        self.assertTrue(res["success"])
        self.assertNotIn("R2", res["path"])
        self.assertEqual(res["path"], ["R1", "R4", "R3", "R5"])

    def test_offline_source_or_dest(self):
        self.graph.load_preset("offline_router")
        # R2 is offline
        res = bfs(self.graph, "R2", "R5")
        self.assertFalse(res["success"])
        res2 = bfs(self.graph, "R1", "R2")
        self.assertFalse(res2["success"])


if __name__ == "__main__":
    unittest.main()
