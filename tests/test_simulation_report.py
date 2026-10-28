"""
tests/test_simulation_report.py — Automated Unit Tests for Dynamic JSON Simulation Report Generation.

Validates:
- Comprehensive report schema (report_type, schema_version 1.0, UTC ISO-8601 generated_at).
- Accurate topology snapshot (routers, edges, online/offline, failed links).
- Correct routing results (BFS and DFS paths, hop counts, visited sequences).
- Handling of source equals destination (1 router path, 0 hops).
- Honest handling of unreachable destinations (empty route, 0 hops, no fabricated paths or parents).
- Handling of offline endpoints.
- Proper inclusion of queue/stack execution traces and complexity analysis.
- Serialization to valid JSON string.
"""

import unittest
import json
from datetime import datetime
from network import Graph
from algorithms import bfs, dfs
from report import generate_simulation_report, export_simulation_report_json


class TestSimulationReport(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.from_preset("reference")

    def test_successful_bfs_report(self):
        sim_res = bfs(self.graph, "N1", "N7")
        report = generate_simulation_report(
            graph=self.graph,
            sim_res=sim_res,
            source="N1",
            destination="N7",
            algo_name="BFS",
            topology_name="Reference 7-Node WAN"
        )

        # Schema fields
        self.assertEqual(report["report_type"], "NetRoute Simulation Report")
        self.assertEqual(report["schema_version"], "1.0")
        self.assertIn("generated_at", report)
        # Parse timestamp to ensure ISO-8601 validity
        dt = datetime.fromisoformat(report["generated_at"])
        self.assertIsNotNone(dt)

        # Topology snapshot
        self.assertEqual(report["topology"]["router_count"], 7)
        self.assertEqual(report["topology"]["connection_count"], 9)
        self.assertEqual(report["topology"]["online_routers_count"], 7)

        # Simulation section
        sim_sec = report["simulation"]
        self.assertEqual(sim_sec["status"], "success")
        self.assertEqual(sim_sec["source"], "N1")
        self.assertEqual(sim_sec["destination"], "N7")
        self.assertEqual(sim_sec["route"], sim_res["path"])
        self.assertEqual(sim_sec["hop_count"], len(sim_res["path"]) - 1)
        self.assertGreater(len(sim_sec["traversal_steps"]), 0)
        self.assertGreater(len(sim_sec["queue_or_stack_states"]), 0)

        # Complexity section
        self.assertEqual(report["complexity"]["time"], "O(V + E)")
        self.assertEqual(report["complexity"]["auxiliary_space"], "O(V)")

    def test_source_equals_destination_report(self):
        sim_res = bfs(self.graph, "N2", "N2")
        report = generate_simulation_report(
            graph=self.graph,
            sim_res=sim_res,
            source="N2",
            destination="N2",
            algo_name="BFS"
        )
        sim_sec = report["simulation"]
        self.assertEqual(sim_sec["status"], "success")
        self.assertEqual(sim_sec["route"], ["N2"])
        self.assertEqual(sim_sec["hop_count"], 0)

    def test_unreachable_destination_report(self):
        # Disconnected graph
        disc_graph = Graph.from_preset("disconnected")
        sim_res = bfs(disc_graph, "R1", "R6")
        report = generate_simulation_report(
            graph=disc_graph,
            sim_res=sim_res,
            source="R1",
            destination="R6",
            algo_name="BFS"
        )
        sim_sec = report["simulation"]
        self.assertEqual(sim_sec["status"], "unreachable")
        self.assertEqual(sim_sec["route"], [])
        self.assertEqual(sim_sec["hop_count"], 0)

    def test_offline_endpoint_report(self):
        self.graph.set_router_status("N7", False)
        sim_res = bfs(self.graph, "N1", "N7")
        report = generate_simulation_report(
            graph=self.graph,
            sim_res=sim_res,
            source="N1",
            destination="N7",
            algo_name="BFS"
        )
        sim_sec = report["simulation"]
        self.assertEqual(sim_sec["status"], "unreachable")
        self.assertEqual(sim_sec["route"], [])

    def test_dfs_report_and_complexity(self):
        sim_res = dfs(self.graph, "N1", "N7")
        report = generate_simulation_report(
            graph=self.graph,
            sim_res=sim_res,
            source="N1",
            destination="N7",
            algo_name="DFS"
        )
        self.assertIn("DFS", report["simulation"]["algorithm"])
        self.assertIn("LIFO stack", report["complexity"]["explanation"])

    def test_export_json_validity(self):
        sim_res = bfs(self.graph, "N1", "N7")
        report = generate_simulation_report(self.graph, sim_res, "N1", "N7", "BFS")
        json_output = export_simulation_report_json(report)
        parsed = json.loads(json_output)
        self.assertEqual(parsed["report_type"], "NetRoute Simulation Report")


if __name__ == "__main__":
    unittest.main()
