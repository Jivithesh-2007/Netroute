"""
test_history_and_report.py — Automated Tests for Simulation History, Replay, and Report Export.
Verifies history recording, replay loading, clearing, and clean CSV/JSON report exports without fabricated data.
"""

import unittest
import json
import streamlit as st
from network import Graph
from algorithms import bfs, dijkstra
import simulation as sim


class TestHistoryAndReport(unittest.TestCase):
    def setUp(self):
        sim.init_session()
        st.session_state["history"] = []
        self.graph = Graph()
        self.graph.load_preset("reference")

    def test_record_history_entry(self):
        """Verifies completed routing experiment is correctly logged into session history."""
        res = bfs(self.graph, "N1", "N7")
        sim.record_history_entry(res, self.graph, "BFS (Breadth First)", "N1", "N7")

        history = sim.get_history()
        self.assertEqual(len(history), 1)
        entry = history[0]
        self.assertEqual(entry["run_id"], 1)
        self.assertEqual(entry["algorithm"], "BFS")
        self.assertEqual(entry["source"], "N1")
        self.assertEqual(entry["destination"], "N7")
        self.assertEqual(entry["route"], ["N1", "N2", "N4", "N6", "N7"])
        self.assertEqual(entry["hops"], 4)
        self.assertTrue(entry["success"])
        self.assertGreater(entry["steps_count"], 0)

    def test_replay_history_run(self):
        """Verifies previous run can be retrieved and loaded into playback state."""
        res = dijkstra(self.graph, "N1", "N7")
        sim.record_history_entry(res, self.graph, "Dijkstra (Minimum-Cost)", "N1", "N7")

        # Invalidate current state
        sim.invalidate_simulation()
        self.assertIsNone(st.session_state["sim_res"])

        # Replay Run 1
        success = sim.replay_history_run(1)
        self.assertTrue(success)
        self.assertIsNotNone(st.session_state["sim_res"])
        self.assertEqual(st.session_state["sim_res"]["path"], ["N1", "N2", "N3", "N5", "N6", "N7"])
        self.assertEqual(st.session_state["step_idx"], 0)
        self.assertTrue(st.session_state["is_playing"])

    def test_clear_history(self):
        """Verifies session history can be safely cleared."""
        res = bfs(self.graph, "N1", "N7")
        sim.record_history_entry(res, self.graph, "BFS", "N1", "N7")
        self.assertEqual(len(sim.get_history()), 1)

        sim.clear_history()
        self.assertEqual(len(sim.get_history()), 0)

    def test_export_json_report(self):
        """Verifies JSON report contains actual metrics without placeholders."""
        res = dijkstra(self.graph, "N1", "N7")
        json_str = sim.export_experiment_report(res, self.graph, "Dijkstra", "N1", "N7", format_type="json")

        data = json.loads(json_str)
        self.assertEqual(data["source"], "N1")
        self.assertEqual(data["destination"], "N7")
        self.assertEqual(data["algorithm"], "Dijkstra (Priority Queue)")
        self.assertEqual(data["route_nodes"], ["N1", "N2", "N3", "N5", "N6", "N7"])
        self.assertEqual(data["total_cost"], 17.0)
        self.assertEqual(data["hop_count"], 5)
        self.assertTrue(data["success"])
        self.assertIn("time_complexity", data)
        self.assertIn("algorithmic_explanation", data)

    def test_export_csv_report(self):
        """Verifies CSV report contains formatted metrics and headers."""
        res = bfs(self.graph, "N1", "N7")
        csv_str = sim.export_experiment_report(res, self.graph, "BFS", "N1", "N7", format_type="csv")

        self.assertIn("Metric,Value", csv_str)
        self.assertIn("Source Node,N1", csv_str)
        self.assertIn("Destination Node,N7", csv_str)
        self.assertIn("Hop Count,4", csv_str)
        self.assertIn("Total Path Cost,19.0", csv_str)

    def test_export_empty_report_handling(self):
        """Verifies report generation handles empty simulation gracefully without crashing."""
        json_str = sim.export_experiment_report(None, self.graph, "BFS", "N1", "N7", format_type="json")
        self.assertEqual(json_str, "{}")

        csv_str = sim.export_experiment_report(None, self.graph, "BFS", "N1", "N7", format_type="csv")
        self.assertIn("Status,No simulation results recorded", csv_str)


if __name__ == "__main__":
    unittest.main()
