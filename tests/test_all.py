import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network import (
    Graph, Router, SimulationStep, SimulationResult,
    bfs_path, dfs_path, grid_maze_bfs, grid_maze_dfs, validate_router_id
)
from algorithms import (
    linear_search, binary_search_iterative, binary_search_recursive, interpolation_search,
    bubble_sort, insertion_sort, selection_sort, merge_sort,
    HashTableChaining, HashTableLinearProbing,
    BinarySearchTree, AVLTree, MinHeap, MaxHeap, BTree,
    inorder_traversal, get_tree_metrics,
    parse_integer, parse_integer_list, get_complexity_info, BenchmarkService
)
from theme import SimulationService


class TestValidationAndServices(unittest.TestCase):
    def test_validate_router_id(self):
        valid, msg = validate_router_id("R1")
        self.assertTrue(valid)
        self.assertEqual(msg, "R1")

        valid, _ = validate_router_id("")
        self.assertFalse(valid)

        valid, _ = validate_router_id("R@#$")
        self.assertFalse(valid)

        valid, _ = validate_router_id("VERYLONGRID12345")
        self.assertFalse(valid)

    def test_parse_integer_list(self):
        valid, nums, _ = parse_integer_list("10, 20 30, 40")
        self.assertTrue(valid)
        self.assertEqual(nums, [10, 20, 30, 40])

        valid, _, _ = parse_integer_list("10, abc, 30")
        self.assertFalse(valid)

        valid, _, _ = parse_integer_list("   ")
        self.assertFalse(valid)

    def test_parse_integer(self):
        valid, val, _ = parse_integer("42")
        self.assertTrue(valid)
        self.assertEqual(val, 42)

        valid, val, _ = parse_integer("abc")
        self.assertFalse(valid)

    def test_simulation_service_controls(self):
        service = SimulationService()
        steps = [
            SimulationStep(step_type="init", message="Step 1"),
            SimulationStep(step_type="compare", message="Step 2")
        ]
        res = SimulationResult(algorithm_name="TestAlg", success=True, steps=steps)

        callback_data = []

        def _on_step(step, current, total):
            callback_data.append((step.message, current, total))

        service.load_simulation(res, on_step=_on_step)
        self.assertEqual(len(service.steps), 2)

        service.step_forward()
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0][0], "Step 1")

        service.step_forward()
        self.assertEqual(len(callback_data), 2)
        self.assertEqual(callback_data[1][0], "Step 2")

        service.set_speed(300)
        self.assertEqual(service.speed_ms, 300)

        service.stop()
        self.assertEqual(service.current_step_index, -1)

    def test_benchmark_service(self):
        sort_res = BenchmarkService.benchmark_sorting([10])
        self.assertIn("Bubble Sort", sort_res)
        self.assertEqual(len(sort_res["Bubble Sort"]), 1)

        search_res = BenchmarkService.benchmark_searching([50])
        self.assertIn("Binary Search", search_res)

        tree_res = BenchmarkService.benchmark_trees(50)
        self.assertIn("BST", tree_res)
        self.assertIn("AVL", tree_res)

    def test_complexity_info(self):
        info = get_complexity_info("BFS Routing")
        self.assertEqual(info["time_worst"], "O(V + E)")

        fallback = get_complexity_info("Unknown Alg")
        self.assertEqual(fallback["time_best"], "N/A")


class TestNetworkFeatures(unittest.TestCase):
    def test_presets_creation(self):
        g_def = Graph.create_default_topology()
        self.assertEqual(len(g_def.routers), 6)
        self.assertTrue(g_def.is_reachable("R1", "R6"))

        g_small = Graph.create_small_connected()
        self.assertEqual(len(g_small.routers), 5)
        self.assertTrue(g_small.is_reachable("R1", "R5"))

        g_med = Graph.create_medium_network()
        self.assertEqual(len(g_med.routers), 9)
        self.assertTrue(g_med.is_reachable("R1", "R9"))

        g_disc = Graph.create_disconnected_network()
        self.assertEqual(len(g_disc.routers), 6)
        comps = g_disc.get_connected_components()
        self.assertEqual(len(comps), 2)
        self.assertFalse(g_disc.is_reachable("R1", "R6"))
        self.assertTrue(g_disc.is_reachable("R1", "R2"))
        self.assertTrue(g_disc.is_reachable("R4", "R6"))

        g_alt = Graph.create_alternate_routes()
        self.assertEqual(len(g_alt.routers), 6)
        bfs_res = bfs_path(g_alt, "R1", "R6")
        dfs_res = dfs_path(g_alt, "R1", "R6")
        self.assertTrue(bfs_res.success)
        self.assertTrue(dfs_res.success)
        self.assertEqual(len(bfs_res.path) - 1, 2)
        self.assertEqual(bfs_res.path, ["R1", "R2", "R6"])

        g_off = Graph.create_offline_scenario()
        self.assertEqual(len(g_off.routers), 5)
        self.assertFalse(g_off.routers["R2"].is_online)
        self.assertTrue(g_off.is_reachable("R1", "R5"))
        bfs_off = bfs_path(g_off, "R1", "R5")
        self.assertTrue(bfs_off.success)
        self.assertEqual(bfs_off.path, ["R1", "R3", "R4", "R5"])

    def test_graph_editing_operations(self):
        g = Graph(directed=False)
        g.add_router(Router("R1", "Router 1", 100, 100))
        g.add_router(Router("R2", "Router 2", 200, 100))
        g.add_router(Router("R3", "Router 3", 300, 100))

        self.assertTrue(g.add_edge("R1", "R2"))
        self.assertTrue(g.add_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 2)
        self.assertTrue(g.is_reachable("R1", "R3"))

        self.assertTrue(g.remove_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 1)
        self.assertFalse(g.is_reachable("R1", "R3"))

        self.assertTrue(g.remove_router("R2"))
        self.assertEqual(len(g.routers), 2)
        self.assertEqual(len(g.get_edges()), 0)
        self.assertNotIn("R2", g.routers)

    def test_reachability_and_offline_toggling(self):
        g = Graph.create_small_connected()
        self.assertTrue(g.is_reachable("R1", "R5"))

        g.set_router_online_status("R2", False)
        g.set_router_online_status("R4", False)

        self.assertFalse(g.is_reachable("R1", "R5"))

        g.set_router_online_status("R4", True)
        self.assertTrue(g.is_reachable("R1", "R5"))

    def test_coordinate_transform_math(self):
        scale = 1.45
        offset_x = 85.0
        offset_y = -35.0

        world_x, world_y = 250.0, 175.0

        screen_x = world_x * scale + offset_x
        screen_y = world_y * scale + offset_y

        inv_world_x = (screen_x - offset_x) / scale
        inv_world_y = (screen_y - offset_y) / scale

        self.assertAlmostEqual(world_x, inv_world_x, places=5)
        self.assertAlmostEqual(world_y, inv_world_y, places=5)


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
        res = bfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertEqual(len(res.path) - 1, 2)

    def test_dfs_valid_path(self):
        res = dfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], "R1")
        self.assertEqual(res.path[-1], "R3")

    def test_single_node_same_src_dest(self):
        res = bfs_path(self.graph, "R1", "R1")
        self.assertTrue(res.success)
        self.assertEqual(res.path, ["R1"])

        res_dfs = dfs_path(self.graph, "R1", "R1")
        self.assertTrue(res_dfs.success)
        self.assertEqual(res_dfs.path, ["R1"])

    def test_disconnected_node(self):
        res = bfs_path(self.graph, "R1", "R5")
        self.assertFalse(res.success)
        self.assertIn("unreachable", res.message.lower())

    def test_offline_router(self):
        self.graph.set_router_online_status("R2", False)
        res = bfs_path(self.graph, "R1", "R3")
        self.assertTrue(res.success)
        self.assertNotIn("R2", res.path)
        self.assertEqual(res.path, ["R1", "R4", "R3"])

    def test_offline_source_or_dest(self):
        self.graph.set_router_online_status("R1", False)
        res_bfs = bfs_path(self.graph, "R1", "R3")
        self.assertFalse(res_bfs.success)

        res_dfs = dfs_path(self.graph, "R2", "R1")
        self.assertFalse(res_dfs.success)

    def test_missing_router_id(self):
        res = bfs_path(self.graph, "NONEXISTENT", "R1")
        self.assertFalse(res.success)

    def test_adjacency_representations(self):
        adj_list = self.graph.get_adjacency_list_view()
        self.assertIn("R2", adj_list["R1"])
        self.assertIn("R4", adj_list["R1"])

        nodes, matrix = self.graph.get_adjacency_matrix_view()
        self.assertEqual(len(nodes), 5)
        self.assertEqual(len(matrix), 5)

    def test_connected_components(self):
        comps = self.graph.get_connected_components()
        self.assertEqual(len(comps), 2)

    def test_grid_maze_bfs_and_dfs(self):
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ]
        res_bfs = grid_maze_bfs(grid, (0, 0), (2, 2))
        self.assertTrue(res_bfs.success)
        self.assertEqual(res_bfs.path[0], (0, 0))
        self.assertEqual(res_bfs.path[-1], (2, 2))

        res_dfs = grid_maze_dfs(grid, (0, 0), (2, 2))
        self.assertTrue(res_dfs.success)
        self.assertEqual(res_dfs.path[0], (0, 0))
        self.assertEqual(res_dfs.path[-1], (2, 2))


class TestSearching(unittest.TestCase):
    def setUp(self):
        self.unsorted_arr = [45, 12, 89, 34, 67, 23, 90, 11]
        self.sorted_arr = [11, 12, 23, 34, 45, 67, 89, 90]
        self.duplicates_arr = [10, 20, 20, 20, 30, 40, 50]
        self.negative_arr = [-50, -20, -10, 0, 10, 30]

    def test_linear_search_found(self):
        res = linear_search(self.unsorted_arr, 67)
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], 4)

    def test_linear_search_not_found(self):
        res = linear_search(self.unsorted_arr, 999)
        self.assertFalse(res.success)

    def test_empty_array(self):
        self.assertFalse(linear_search([], 10).success)
        self.assertFalse(binary_search_iterative([], 10).success)
        self.assertFalse(binary_search_recursive([], 10).success)
        self.assertFalse(interpolation_search([], 10).success)

    def test_single_element_array(self):
        self.assertTrue(linear_search([42], 42).success)
        self.assertTrue(binary_search_iterative([42], 42).success)
        self.assertTrue(binary_search_recursive([42], 42).success)
        self.assertTrue(interpolation_search([42], 42).success)
        self.assertFalse(binary_search_iterative([42], 99).success)

    def test_unsorted_validation(self):
        self.assertFalse(binary_search_iterative(self.unsorted_arr, 34).success)
        self.assertFalse(binary_search_recursive(self.unsorted_arr, 34).success)
        self.assertFalse(interpolation_search(self.unsorted_arr, 34).success)

    def test_binary_search_iterative(self):
        res = binary_search_iterative(self.sorted_arr, 34)
        self.assertTrue(res.success)
        self.assertEqual(self.sorted_arr[res.path[0]], 34)

    def test_binary_search_recursive(self):
        res = binary_search_recursive(self.sorted_arr, 89)
        self.assertTrue(res.success)
        self.assertEqual(self.sorted_arr[res.path[0]], 89)

    def test_interpolation_search(self):
        res = interpolation_search(self.sorted_arr, 45)
        self.assertTrue(res.success)
        self.assertEqual(self.sorted_arr[res.path[0]], 45)

    def test_interpolation_search_duplicates(self):
        res = interpolation_search(self.duplicates_arr, 20)
        self.assertTrue(res.success)

    def test_negative_values(self):
        res = binary_search_iterative(self.negative_arr, -20)
        self.assertTrue(res.success)
        self.assertEqual(self.negative_arr[res.path[0]], -20)


class TestSorting(unittest.TestCase):
    def setUp(self):
        self.unsorted = [64, 34, 25, 12, 22, 11, 90]
        self.expected = [11, 12, 22, 25, 34, 64, 90]
        self.already_sorted = [1, 2, 3, 4, 5]
        self.reverse_sorted = [5, 4, 3, 2, 1]
        self.duplicates = [5, 2, 5, 1, 2, 8, 5]
        self.negatives = [-10, 5, -20, 0, 15]

    def test_bubble_sort(self):
        res = bubble_sort(self.unsorted)
        self.assertEqual(res.path, self.expected)

    def test_insertion_sort(self):
        res = insertion_sort(self.unsorted)
        self.assertEqual(res.path, self.expected)

    def test_selection_sort(self):
        res = selection_sort(self.unsorted)
        self.assertEqual(res.path, self.expected)

    def test_merge_sort(self):
        res = merge_sort(self.unsorted)
        self.assertEqual(res.path, self.expected)

    def test_empty_array(self):
        self.assertEqual(bubble_sort([]).path, [])
        self.assertEqual(insertion_sort([]).path, [])
        self.assertEqual(selection_sort([]).path, [])
        self.assertEqual(merge_sort([]).path, [])

    def test_single_value(self):
        self.assertEqual(bubble_sort([42]).path, [42])
        self.assertEqual(insertion_sort([42]).path, [42])
        self.assertEqual(selection_sort([42]).path, [42])
        self.assertEqual(merge_sort([42]).path, [42])

    def test_duplicates(self):
        expected = [1, 2, 2, 5, 5, 5, 8]
        self.assertEqual(bubble_sort(self.duplicates).path, expected)
        self.assertEqual(insertion_sort(self.duplicates).path, expected)
        self.assertEqual(selection_sort(self.duplicates).path, expected)
        self.assertEqual(merge_sort(self.duplicates).path, expected)

    def test_negatives(self):
        expected = [-20, -10, 0, 5, 15]
        self.assertEqual(merge_sort(self.negatives).path, expected)

    def test_already_sorted_input(self):
        self.assertEqual(bubble_sort(self.already_sorted).path, self.already_sorted)
        self.assertEqual(insertion_sort(self.already_sorted).path, self.already_sorted)

    def test_reverse_sorted_input(self):
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(merge_sort(self.reverse_sorted).path, expected)


class TestHashing(unittest.TestCase):
    def test_separate_chaining(self):
        table = HashTableChaining(size=5)
        table.insert(10)
        table.insert(15)

        res = table.search(15)
        self.assertTrue(res.success)
        self.assertEqual(table.collisions, 1)

        del_res = table.delete(10)
        self.assertTrue(del_res.success)

        res_after = table.search(15)
        self.assertTrue(res_after.success)

        self.assertFalse(table.search(999).success)
        self.assertFalse(table.delete(999).success)

        table.clear()
        self.assertEqual(table.item_count, 0)

    def test_linear_probing_tombstones(self):
        table = HashTableLinearProbing(size=5)
        table.insert(10)
        table.insert(15)
        table.insert(20)

        table.delete(15)
        self.assertEqual(table.table[1], table.DELETED)

        res = table.search(20)
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], 2)

    def test_linear_probing_full_table(self):
        table = HashTableLinearProbing(size=3)
        self.assertTrue(table.insert(1).success)
        self.assertTrue(table.insert(2).success)
        self.assertTrue(table.insert(3).success)

        res_full = table.insert(4)
        self.assertFalse(res_full.success)
        self.assertIn("full", res_full.message.lower())

    def test_linear_probing_delete_miss(self):
        table = HashTableLinearProbing(size=5)
        table.insert(10)
        self.assertFalse(table.delete(999).success)


class TestBST(unittest.TestCase):
    def test_bst_operations(self):
        bst = BinarySearchTree()
        keys = [50, 30, 70, 20, 40, 60, 80]
        for k in keys:
            bst.insert(k)

        seq, _ = inorder_traversal(bst.root)
        self.assertEqual(seq, sorted(keys))

        self.assertTrue(bst.search(40).success)
        self.assertFalse(bst.search(99).success)

        self.assertEqual(bst.find_min(), 20)
        self.assertEqual(bst.find_max(), 80)

        self.assertFalse(bst.insert(50).success)

        self.assertTrue(bst.delete(20).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(20, seq)

        bst.insert(25)
        self.assertTrue(bst.delete(30).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(30, seq)
        self.assertIn(25, seq)

        self.assertTrue(bst.delete(50).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(50, seq)

        self.assertFalse(bst.delete(999).success)

        bst.clear()
        self.assertIsNone(bst.root)


class TestAVL(unittest.TestCase):
    def test_avl_rotations_and_balance(self):
        avl = AVLTree()
        for k in [10, 20, 30, 40, 50, 25]:
            avl.insert(k)

        seq, _ = inorder_traversal(avl.root)
        self.assertEqual(seq, [10, 20, 25, 30, 40, 50])

        h, total, _ = get_tree_metrics(avl.root)
        self.assertLessEqual(h, 4)
        self.assertEqual(total, 6)

        def _check_balance(node):
            if not node:
                return True
            bf = node.get_balance_factor()
            self.assertIn(bf, [-1, 0, 1])
            return _check_balance(node.left) and _check_balance(node.right)

        _check_balance(avl.root)

    def test_avl_deletion_and_rebalance(self):
        avl = AVLTree()
        for k in [10, 20, 30, 40, 50]:
            avl.insert(k)

        self.assertTrue(avl.delete(50).success)
        self.assertFalse(avl.search(50).success)
        self.assertFalse(avl.delete(999).success)


class TestHeap(unittest.TestCase):
    def test_min_heap(self):
        heap = MinHeap()
        for v in [50, 20, 40, 10, 30]:
            heap.insert(v)

        self.assertEqual(heap.peek(), 10)

        extracted = []
        while heap.heap:
            val, _ = heap.extract_min()
            extracted.append(val)

        self.assertEqual(extracted, [10, 20, 30, 40, 50])

    def test_empty_heap(self):
        heap = MinHeap()
        self.assertIsNone(heap.peek())
        val, res = heap.extract_min()
        self.assertIsNone(val)
        self.assertFalse(res.success)

    def test_build_heap(self):
        heap = MinHeap()
        heap.build_heap([90, 40, 10, 30, 20])
        self.assertEqual(heap.peek(), 10)

    def test_max_heap(self):
        heap = MaxHeap()
        for v in [50, 20, 40, 10, 30]:
            heap.insert(v)

        self.assertEqual(heap.peek(), 50)
        val, res = heap.extract_max()
        self.assertEqual(val, 50)


class TestBTree(unittest.TestCase):
    def test_b_tree_insert_search(self):
        tree = BTree(t=2)
        keys = [10, 20, 30, 40, 50, 60, 70]
        for k in keys:
            tree.insert(k)

        for k in keys:
            self.assertTrue(tree.search(k).success)

        self.assertFalse(tree.search(999).success)

    def test_b_tree_deletion(self):
        tree = BTree(t=2)
        keys = [10, 20, 30, 40, 50, 60, 70]
        for k in keys:
            tree.insert(k)

        res_del = tree.delete(30)
        self.assertTrue(res_del.success)
        self.assertFalse(tree.search(30).success)
        self.assertFalse(tree.delete(999).success)

    def test_empty_b_tree(self):
        tree = BTree(t=2)
        self.assertFalse(tree.search(10).success)
        self.assertFalse(tree.delete(10).success)


class TestNetworkFeatures(unittest.TestCase):
    def test_presets_creation(self):
        g_def = Graph.create_default_topology()
        self.assertEqual(len(g_def.routers), 6)
        self.assertTrue(g_def.is_reachable("R1", "R6"))

        g_small = Graph.create_small_connected()
        self.assertEqual(len(g_small.routers), 5)
        self.assertTrue(g_small.is_reachable("R1", "R5"))

        g_med = Graph.create_medium_network()
        self.assertEqual(len(g_med.routers), 9)
        self.assertTrue(g_med.is_reachable("R1", "R9"))

        g_disc = Graph.create_disconnected_network()
        self.assertEqual(len(g_disc.routers), 6)
        comps = g_disc.get_connected_components()
        self.assertEqual(len(comps), 2)
        self.assertFalse(g_disc.is_reachable("R1", "R6"))
        self.assertTrue(g_disc.is_reachable("R1", "R2"))
        self.assertTrue(g_disc.is_reachable("R4", "R6"))

        g_alt = Graph.create_alternate_routes()
        self.assertEqual(len(g_alt.routers), 6)
        bfs_res = bfs_path(g_alt, "R1", "R6")
        dfs_res = dfs_path(g_alt, "R1", "R6")
        self.assertTrue(bfs_res.success)
        self.assertTrue(dfs_res.success)
        self.assertEqual(len(bfs_res.path) - 1, 2)
        self.assertEqual(bfs_res.path, ["R1", "R2", "R6"])

        g_off = Graph.create_offline_scenario()
        self.assertEqual(len(g_off.routers), 5)
        self.assertFalse(g_off.routers["R2"].is_online)
        self.assertTrue(g_off.is_reachable("R1", "R5"))
        bfs_off = bfs_path(g_off, "R1", "R5")
        self.assertTrue(bfs_off.success)
        self.assertEqual(bfs_off.path, ["R1", "R3", "R4", "R5"])

    def test_graph_editing_operations(self):
        g = Graph(directed=False)
        g.add_router(Router("R1", "Router 1", 100, 100))
        g.add_router(Router("R2", "Router 2", 200, 100))
        g.add_router(Router("R3", "Router 3", 300, 100))

        self.assertTrue(g.add_edge("R1", "R2"))
        self.assertTrue(g.add_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 2)
        self.assertTrue(g.is_reachable("R1", "R3"))

        self.assertTrue(g.remove_edge("R2", "R3"))
        self.assertEqual(len(g.get_edges()), 1)
        self.assertFalse(g.is_reachable("R1", "R3"))

        self.assertTrue(g.remove_router("R2"))
        self.assertEqual(len(g.routers), 2)
        self.assertEqual(len(g.get_edges()), 0)
        self.assertNotIn("R2", g.routers)

    def test_reachability_and_offline_toggling(self):
        g = Graph.create_small_connected()
        self.assertTrue(g.is_reachable("R1", "R5"))

        g.set_router_online_status("R2", False)
        g.set_router_online_status("R4", False)

        self.assertFalse(g.is_reachable("R1", "R5"))

        g.set_router_online_status("R4", True)
        self.assertTrue(g.is_reachable("R1", "R5"))

    def test_coordinate_transform_math(self):
        scale = 1.45
        offset_x = 85.0
        offset_y = -35.0

        world_x, world_y = 250.0, 175.0

        screen_x = world_x * scale + offset_x
        screen_y = world_y * scale + offset_y

        inv_world_x = (screen_x - offset_x) / scale
        inv_world_y = (screen_y - offset_y) / scale

        self.assertAlmostEqual(world_x, inv_world_x, places=5)
        self.assertAlmostEqual(world_y, inv_world_y, places=5)


if __name__ == "__main__":
    unittest.main()
