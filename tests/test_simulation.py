"""
Unit tests for simulation.py (step playback, packet hop progression, state reset).
"""

import unittest
from unittest.mock import patch
from network import Graph
from algorithms import bfs
import simulation as sim


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.mock_state = {}

    def test_step_navigation_boundaries(self):
        graph = Graph()
        graph.load_preset("direct")
        res = bfs(graph, "R1", "R4")

        # Mock streamlit session_state
        with patch.object(sim, "st") as mock_st:
            mock_st.session_state = {
                "sim_res": res,
                "step_idx": 0,
                "packet_hop": 0,
                "auto_play": False,
                "packet_auto": False
            }

            total_steps = len(res["steps"])
            self.assertGreater(total_steps, 0)

            # Backward from 0 should stay at 0
            sim.step_backward()
            self.assertEqual(mock_st.session_state["step_idx"], 0)

            # Forward moves to 1
            sim.step_forward()
            self.assertEqual(mock_st.session_state["step_idx"], 1)

            # Jump to last step
            sim.jump_to_step(total_steps - 1)
            self.assertEqual(mock_st.session_state["step_idx"], total_steps - 1)

            # Forward past end should stay at last step
            sim.step_forward()
            self.assertEqual(mock_st.session_state["step_idx"], total_steps - 1)

            # Reset visualizer
            sim.reset_playback()
            self.assertEqual(mock_st.session_state["step_idx"], 0)

    def test_packet_transmission_hops(self):
        graph = Graph()
        graph.load_preset("direct")
        res = bfs(graph, "R1", "R4")  # path: R1, R2, R3, R4 (3 hops)

        with patch.object(sim, "st") as mock_st:
            mock_st.session_state = {
                "sim_res": res,
                "packet_hop": 0,
                "packet_auto": False
            }

            # Step 1 -> Hop 1 (at R2)
            sim.packet_step_forward()
            self.assertEqual(mock_st.session_state["packet_hop"], 1)

            # Step 2 -> Hop 2 (at R3)
            sim.packet_step_forward()
            self.assertEqual(mock_st.session_state["packet_hop"], 2)

            # Step 3 -> Hop 3 (at R4, destination)
            sim.packet_step_forward()
            self.assertEqual(mock_st.session_state["packet_hop"], 3)

            # Step 4 past destination should stay at destination
            sim.packet_step_forward()
            self.assertEqual(mock_st.session_state["packet_hop"], 3)

            # Reset packet
            sim.reset_packet()
            self.assertEqual(mock_st.session_state["packet_hop"], 0)


if __name__ == "__main__":
    unittest.main()
