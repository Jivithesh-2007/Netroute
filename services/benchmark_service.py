"""
Benchmarking service for empirical performance evaluation of algorithms.
Runs real Python algorithm implementations across multiple dataset sizes.
"""
import random
import time
from typing import Dict, List, Any
from algorithms.searching import linear_search, binary_search_iterative, interpolation_search
from algorithms.sorting import bubble_sort, insertion_sort, selection_sort, merge_sort
from algorithms.hashing import HashTableChaining, HashTableLinearProbing
from algorithms.binary_search_tree import BinarySearchTree
from algorithms.avl_tree import AVLTree


class BenchmarkService:
    """Provides empirical benchmarking for CO3, CO4, and CO5 algorithms."""

    @staticmethod
    def benchmark_sorting(sizes: List[int] = [10, 50, 100, 200]) -> Dict[str, List[Dict[str, Any]]]:
        """Benchmark sorting algorithms on random arrays."""
        results = {
            "Bubble Sort": [],
            "Insertion Sort": [],
            "Selection Sort": [],
            "Merge Sort": []
        }

        random.seed(42)  # Deterministic seed for reproducible benchmarking

        for size in sizes:
            arr = [random.randint(1, 1000) for _ in range(size)]

            # Bubble Sort
            res = bubble_sort(arr)
            results["Bubble Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            # Insertion Sort
            res = insertion_sort(arr)
            results["Insertion Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            # Selection Sort
            res = selection_sort(arr)
            results["Selection Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            # Merge Sort
            res = merge_sort(arr)
            results["Merge Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

        return results

    @staticmethod
    def benchmark_searching(sizes: List[int] = [100, 500, 1000, 2000]) -> Dict[str, List[Dict[str, Any]]]:
        """Benchmark searching algorithms on sorted arrays."""
        results = {
            "Linear Search": [],
            "Binary Search": [],
            "Interpolation Search": []
        }

        random.seed(42)

        for size in sizes:
            arr = sorted([random.randint(1, 10000) for _ in range(size)])
            target = arr[size // 2]  # Target present in middle

            # Linear Search
            res = linear_search(arr, target)
            results["Linear Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

            # Binary Search
            res = binary_search_iterative(arr, target)
            results["Binary Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

            # Interpolation Search
            res = interpolation_search(arr, target)
            results["Interpolation Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

        return results

    @staticmethod
    def benchmark_trees(num_ops: int = 500) -> Dict[str, Dict[str, Any]]:
        """Benchmark BST vs AVL Tree operations."""
        random.seed(42)
        keys = list(range(num_ops))  # Sequential keys produce skewed BST, balanced AVL

        # BST Sequential Insertion
        bst = BinarySearchTree()
        t0 = time.perf_counter()
        for k in keys:
            bst.insert(k)
        bst_insert_time = (time.perf_counter() - t0) * 1000

        # BST Search Worst Case
        res_bst = bst.search(keys[-1])

        # AVL Sequential Insertion
        avl = AVLTree()
        t0 = time.perf_counter()
        for k in keys:
            avl.insert(k)
        avl_insert_time = (time.perf_counter() - t0) * 1000

        # AVL Search Worst Case
        res_avl = avl.search(keys[-1])

        return {
            "BST": {
                "num_ops": num_ops,
                "insert_time_ms": bst_insert_time,
                "search_comparisons": res_bst.total_comparisons,
                "search_time_ms": res_bst.execution_time_ms
            },
            "AVL": {
                "num_ops": num_ops,
                "insert_time_ms": avl_insert_time,
                "search_comparisons": res_avl.total_comparisons,
                "search_time_ms": res_avl.execution_time_ms
            }
        }
