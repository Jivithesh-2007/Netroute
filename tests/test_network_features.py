"""
Unit tests for new Network Simulator features, topology editing, presets,
reachability analysis, and coordinate transformations.
"""
import unittest
from models.graph import Graph
from models.router import Router
from algorithms.graph_algorithms import bfs_path, dfs_path


class TestNetworkFeatures(unittest.TestCase):
    """Test suite for graph presets, editing, reachability, and topology validation."""

    def test_presets_creation(self):
        """Verify all graph preset topologies are valid, connected, or partitioned as specified."""
        # 1. Default Topology
        g_def = Graph.create_default_topology()
        self.assertEqual(len(g_def.routers), 6)
        self.assertTrue(g_def.is_reachable("R1", "R6"))

        # 2. Small Connected
        g_small = Graph.create_small_connected()
        self.assertEqual(len(g_small.routers), 5)
        self.assertTrue(g_small.is_reachable("R1", "R5"))

        # 3. Medium Network
        g_med = Graph.create_medium_network()
        self.assertEqual(len(g_med.routers), 9)
        self.assertTrue(g_med.is_reachable("R1", "R9"))

        # 4. Disconnected Network (2 components)
        g_disc = Graph.create_disconnected_network()
        self.assertEqual(len(g_disc.routers), 6)
        comps = g_disc.get_connected_components()
        self.assertEqual(len(comps), 2)
        # R1 in component 1 cannot reach R6 in component 2
        self.assertFalse(g_disc.is_reachable("R1", "R6"))
        self.assertTrue(g_disc.is_reachable("R1", "R2"))
        self.assertTrue(g_disc.is_reachable("R4", "R6"))

        # 5. Alternate Routes (Demonstrating BFS vs DFS difference)
        g_alt = Graph.create_alternate_routes()
        self.assertEqual(len(g_alt.routers), 6)
        bfs_res = bfs_path(g_alt, "R1", "R6")
        dfs_res = dfs_path(g_alt, "R1", "R6")
        self.assertTrue(bfs_res.success)
        self.assertTrue(dfs_res.success)
        # BFS must find shortest hop path (2 hops: R1 -> R2 -> R6)
        self.assertEqual(len(bfs_res.path) - 1, 2)
        self.assertEqual(bfs_res.path, ["R1", "R2", "R6"])

        # 6. Offline Bottleneck Scenario
        g_off = Graph.create_offline_scenario()
        self.assertEqual(len(g_off.routers), 5)
        self.assertFalse(g_off.routers["R2"].is_online)
        # Still reachable via backup path R1 -> R3 -> R4 -> R5
        self.assertTrue(g_off.is_reachable("R1", "R5"))
        bfs_off = bfs_path(g_off, "R1", "R5")
        self.assertTrue(bfs_off.success)
        self.assertEqual(bfs_off.path, ["R1", "R3", "R4", "R5"])

    def test_graph_editing_operations(self):
        """Verify dynamic router addition, deletion, link creation, and link removal."""
        g = Graph(directed=False)
        g.add_router(Router("R1", "Router 1", 100, 100))
        g.add_router(Router("R2", "Router 2", 200, 100))
        g.add_router(Router("R3", "Router 3", 300, 100))

        # Add edges
        self.assertTrue(g.add_edge("R1", "R2"))
        self.assertTrue(g.add_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 2)
        self.assertTrue(g.is_reachable("R1", "R3"))

        # Remove edge
        self.assertTrue(g.remove_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 1)
        self.assertFalse(g.is_reachable("R1", "R3"))

        # Delete router
        self.assertTrue(g.remove_router("R2"))
        self.assertEqual(len(g.routers), 2)
        self.assertEqual(len(g.get_edges()), 0)
        self.assertNotIn("R2", g.routers)

    def test_reachability_and_offline_toggling(self):
        """Verify is_reachable correctly respects online/offline router statuses."""
        g = Graph.create_small_connected()
        self.assertTrue(g.is_reachable("R1", "R5"))

        # Take both intermediate branches offline
        g.set_router_online_status("R2", False)
        g.set_router_online_status("R4", False)

        # Now R5 is completely unreachable from R1
        self.assertFalse(g.is_reachable("R1", "R5"))

        # Bring R4 back online
        g.set_router_online_status("R4", True)
        self.assertTrue(g.is_reachable("R1", "R5"))

    def test_coordinate_transform_math(self):
        """Verify scale and pan coordinate transformation invertibility."""
        scale = 1.45
        offset_x = 85.0
        offset_y = -35.0

        world_x, world_y = 250.0, 175.0

        # World to screen
        screen_x = world_x * scale + offset_x
        screen_y = world_y * scale + offset_y

        # Screen to world (inverse)
        inv_world_x = (screen_x - offset_x) / scale
        inv_world_y = (screen_y - offset_y) / scale

        self.assertAlmostEqual(world_x, inv_world_x, places=5)
        self.assertAlmostEqual(world_y, inv_world_y, places=5)


if __name__ == "__main__":
    unittest.main()
