"""
Unit tests for graph algorithms (BFS, DFS, Connectivity, Adjacency representations).
"""
import unittest
from models.graph import Graph
from models.router import Router
from algorithms.graph_algorithms import bfs_path, dfs_path, grid_maze_bfs, grid_maze_dfs


class TestGraphAlgorithms(unittest.TestCase):

    def setUp(self):
        self.graph = Graph(directed=False)
        self.graph.add_router(Router("R1", "Core R1", 100, 100))
        self.graph.add_router(Router("R2", "Edge R2", 200, 100))
        self.graph.add_router(Router("R3", "Gateway R3", 300, 100))
        self.graph.add_router(Router("R4", "Distributor R4", 200, 200))
        self.graph.add_router(Router("R5", "Isolated R5", 400, 400))

        self.graph.add_edge("R1", "R2")
        self.graph.add_edge("R2", "R3")
        self.graph.add_edge("R1", "R4")
        self.graph.add_edge("R4", "R3")

    def test_bfs_shortest_path(self):
        """Test BFS finds shortest hop route."""
        res = bfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertEqual(len(res.path) - 1, 2)  # R1 -> R2 -> R3 or R1 -> R4 -> R3

    def test_dfs_valid_path(self):
        """Test DFS returns a valid path."""
        res = dfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], "R1")
        self.assertEqual(res.path[-1], "R3")

    def test_disconnected_node(self):
        """Test unreachable node handling."""
        res = bfs_path(self.graph, "R1", "R5")
        self.assertFalse(res.success)
        self.assertIn("unreachable", res.message.lower())

    def test_offline_router(self):
        """Test offline router is not traversed."""
        self.graph.set_router_online_status("R2", False)
        res = bfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertNotIn("R2", res.path)
        self.assertEqual(res.path, ["R1", "R4", "R3"])

    def test_adjacency_representations(self):
        """Test Adjacency List and Matrix views."""
        adj_list = self.graph.get_adjacency_list_view()
        self.assertIn("R2", adj_list["R1"])
        self.assertIn("R4", adj_list["R1"])

        nodes, matrix = self.graph.get_adjacency_matrix_view()
        self.assertEqual(len(nodes), 5)
        self.assertEqual(len(matrix), 5)

    def test_grid_maze_bfs(self):
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ]
        res = grid_maze_bfs(grid, (0, 0), (2, 2))
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], (0, 0))
        self.assertEqual(res.path[-1], (2, 2))


if __name__ == "__main__":
    unittest.main()
