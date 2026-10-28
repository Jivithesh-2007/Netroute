"""
tests/test_reports_and_features.py — Automated tests for new features:
- Simulation JSON report generation (single and dual comparison)
- Strict topology validation and serialization integrity
- Dual comparison simulation state and synchronized stepping
- Simulation history recording
- Visualizer figure generation
"""

import json
import unittest
from unittest.mock import patch

from network import Graph, validate_router_id
from algorithms import (
    bfs, dfs, compare_bfs_dfs,
    generate_simulation_report, generate_comparison_report
)
import simulation as sim
from visualizer import build_network_figure, build_traversal_tree_figure, build_algo_result_figure


class TestSimulationReports(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.from_preset("reference")

    def test_single_bfs_report_valid_json(self):
        res = bfs(self.graph, "N1", "N7")
        report = generate_simulation_report(self.graph, res, "N1", "N7")

        # Must serialize to JSON without error
        json_str = json.dumps(report)
        self.assertIsInstance(json_str, str)

        parsed = json.loads(json_str)
        self.assertEqual(parsed["schema_version"], "1.0.0")
        self.assertEqual(parsed["endpoints"]["source"], "N1")
        self.assertEqual(parsed["endpoints"]["destination"], "N7")
        self.assertEqual(parsed["status"], "SUCCESS")
        self.assertIn("route", parsed)
        self.assertEqual(parsed["route"]["hop_count"], res["hops"])
        self.assertIn("metrics", parsed)
        self.assertIn("topology_snapshot", parsed)
        self.assertIn("step_by_step_trace", parsed)
        self.assertGreater(len(parsed["step_by_step_trace"]), 0)

    def test_single_dfs_report_valid_json(self):
        res = dfs(self.graph, "N1", "N7")
        report = generate_simulation_report(self.graph, res, "N1", "N7")
        json_str = json.dumps(report)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["status"], "SUCCESS")
        self.assertIn("DFS", parsed["algorithm"])

    def test_unreachable_destination_report(self):
        disc_graph = Graph.from_preset("disconnected")
        res = bfs(disc_graph, "R1", "R4")
        report = generate_simulation_report(disc_graph, res, "R1", "R4")

        self.assertEqual(report["status"], "NO_ROUTE_FOUND")
        self.assertEqual(report["route"]["hop_count"], 0)
        self.assertEqual(report["route"]["path"], [])

    def test_dual_comparison_report(self):
        cmp_res = compare_bfs_dfs(self.graph, "N1", "N7")
        report = generate_comparison_report(self.graph, cmp_res, "N1", "N7")

        json_str = json.dumps(report)
        parsed = json.loads(json_str)

        self.assertEqual(parsed["report_type"], "DUAL_ALGORITHM_COMPARISON")
        self.assertIn("comparison_summary", parsed)
        self.assertIn("bfs_run", parsed)
        self.assertIn("dfs_run", parsed)
        self.assertIn("winner", parsed["comparison_summary"])
        self.assertEqual(parsed["bfs_run"]["endpoints"]["source"], "N1")
        self.assertEqual(parsed["dfs_run"]["endpoints"]["destination"], "N7")


class TestTopologyValidation(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_reject_invalid_json_types(self):
        ok, msg = self.graph.load_from_dict("not a dict")
        self.assertFalse(ok)
        self.assertIn("JSON root must be an object", msg)

        ok, msg = self.graph.load_from_dict({"routers": "not a list", "edges": []})
        self.assertFalse(ok)
        self.assertIn("'routers' list is required", msg)

    def test_reject_invalid_router_id(self):
        bad_data = {
            "routers": [{"id": "INVALID LONG ID"}],
            "edges": []
        }
        ok, msg = self.graph.load_from_dict(bad_data)
        self.assertFalse(ok)
        self.assertIn("Invalid router ID", msg)

    def test_reject_duplicate_router_id(self):
        dup_data = {
            "routers": [{"id": "R1"}, {"id": "R1"}],
            "edges": []
        }
        ok, msg = self.graph.load_from_dict(dup_data)
        self.assertFalse(ok)
        self.assertIn("Duplicate router ID", msg)

    def test_reject_self_loop_edge(self):
        loop_data = {
            "routers": [{"id": "R1"}],
            "edges": [["R1", "R1", 1.0]]
        }
        ok, msg = self.graph.load_from_dict(loop_data)
        self.assertFalse(ok)
        self.assertIn("Self-loop edge", msg)

    def test_reject_negative_weight(self):
        neg_data = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "R2", -5.0]]
        }
        ok, msg = self.graph.load_from_dict(neg_data)
        self.assertFalse(ok)
        self.assertIn("negative weight", msg)

    def test_failed_import_does_not_corrupt_existing_graph(self):
        self.graph.add_router("ORIGINAL")
        self.assertIn("ORIGINAL", self.graph.routers)

        bad_data = {
            "routers": [{"id": "R1"}, {"id": "R2"}],
            "edges": [["R1", "R3"]]  # R3 doesn't exist
        }
        ok, msg = self.graph.load_from_dict(bad_data)
        self.assertFalse(ok)
        # Graph MUST retain its original state
        self.assertIn("ORIGINAL", self.graph.routers)
        self.assertNotIn("R1", self.graph.routers)

    def test_round_trip_export_and_import(self):
        g1 = Graph.from_preset("reference")
        exported = g1.to_dict()

        g2 = Graph()
        ok, msg = g2.load_from_dict(exported)
        self.assertTrue(ok)
        self.assertEqual(len(g1.routers), len(g2.routers))
        self.assertEqual(len(g1.get_edges()), len(g2.get_edges()))
        self.assertEqual(g1.get_edges(), g2.get_edges())


class TestDualComparisonAndHistory(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.from_preset("reference")

    def test_dual_comparison_execution(self):
        with patch.object(sim, "st") as mock_st:
            mock_st.session_state = {
                "cmp_res": None,
                "cmp_step_idx": 0,
                "simulation_history": []
            }

            cmp_res = sim.execute_dual_comparison(self.graph, "N1", "N7")
            self.assertIsNotNone(mock_st.session_state["cmp_res"])
            self.assertEqual(mock_st.session_state["cmp_step_idx"], 0)
            self.assertGreater(len(mock_st.session_state["simulation_history"]), 0)

            # Test comparison step forward
            bfs_len = len(cmp_res["bfs"]["steps"])
            dfs_len = len(cmp_res["dfs"]["steps"])
            max_len = max(bfs_len, dfs_len)

            sim.cmp_step_forward()
            self.assertEqual(mock_st.session_state["cmp_step_idx"], 1)

            sim.cmp_step_backward()
            self.assertEqual(mock_st.session_state["cmp_step_idx"], 0)

            sim.cmp_last_step()
            self.assertEqual(mock_st.session_state["cmp_step_idx"], max_len - 1)

            sim.cmp_reset()
            self.assertEqual(mock_st.session_state["cmp_step_idx"], 0)

    def test_step_visual_state_bounds(self):
        res = bfs(self.graph, "N1", "N7")
        state_0 = sim.get_step_visual_state(self.graph, res, 0)
        self.assertEqual(state_0["active_node"], "N1")
        self.assertFalse(state_0["is_completed"])

        last_idx = len(res["steps"]) - 1
        state_end = sim.get_step_visual_state(self.graph, res, last_idx)
        self.assertTrue(state_end["is_completed"])
        self.assertEqual(state_end["route_nodes"], set(res["path"]))

        # Out-of-bounds index should clamp safely
        state_clamped = sim.get_step_visual_state(self.graph, res, 99999)
        self.assertTrue(state_clamped["is_completed"])


class TestVisualizerFigures(unittest.TestCase):
    def setUp(self):
        self.graph = Graph.from_preset("reference")

    def test_build_network_figure(self):
        res = bfs(self.graph, "N1", "N7")
        active = sim.get_step_visual_state(self.graph, res, 0)
        fig = build_network_figure(self.graph, active, "N1", "N7")
        self.assertIsNotNone(fig)
        self.assertGreater(len(fig.data), 0)

    def test_build_traversal_tree_figure(self):
        res = bfs(self.graph, "N1", "N7")
        from algorithms import build_traversal_tree
        tree_data = build_traversal_tree(res["parents"], "N1", "N7")
        fig = build_traversal_tree_figure(tree_data, "N1", "N7")
        self.assertIsNotNone(fig)
        self.assertGreater(len(fig.data), 0)

    def test_build_algo_result_figure(self):
        res = bfs(self.graph, "N1", "N7")
        fig = build_algo_result_figure(self.graph, res, "N1", "N7")
        self.assertIsNotNone(fig)
        self.assertGreater(len(fig.data), 0)
