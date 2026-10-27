"""
test_co3_searching_sorting.py — Automated Unit Tests for CO3 Searching & Sorting Algorithms.

Validates:
- Linear search (present, absent, empty, comparison counter).
- Binary search (present, absent, empty, unsorted rejection, comparison counter).
- Bubble sort (correctness against sorted(), comparisons, swaps, empty/single).
- Insertion sort (correctness against sorted(), comparisons, shifts, empty/single).
"""

import unittest
from algorithms import linear_search, binary_search, bubble_sort, insertion_sort


class TestCO3SearchingSorting(unittest.TestCase):
    def setUp(self):
        self.router_ids = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
        self.unsorted_ids = ["R4", "R1", "R7", "R2", "R6", "R3", "R5"]

    # -------------------------------------------------------------
    # Linear Search Tests
    # -------------------------------------------------------------
    def test_linear_search_present(self):
        res = linear_search(self.unsorted_ids, "R2")
        self.assertTrue(res["found"])
        self.assertEqual(res["target"], "R2")
        self.assertEqual(res["index"], 3)
        self.assertEqual(res["comparisons"], 4)
        self.assertEqual(res["theoretical_complexity"], "O(n)")

    def test_linear_search_absent(self):
        res = linear_search(self.unsorted_ids, "R99")
        self.assertFalse(res["found"])
        self.assertEqual(res["index"], -1)
        self.assertEqual(res["comparisons"], len(self.unsorted_ids))

    def test_linear_search_empty(self):
        res = linear_search([], "R1")
        self.assertFalse(res["found"])
        self.assertEqual(res["index"], -1)
        self.assertEqual(res["comparisons"], 0)

    # -------------------------------------------------------------
    # Binary Search Tests
    # -------------------------------------------------------------
    def test_binary_search_sorted_present(self):
        res = binary_search(self.router_ids, "R4")
        self.assertTrue(res["found"])
        self.assertEqual(res["index"], 3)
        self.assertGreater(res["comparisons"], 0)
        self.assertLessEqual(res["comparisons"], 4)  # log2(7) is < 3
        self.assertEqual(res["theoretical_complexity"], "O(log n)")

    def test_binary_search_absent(self):
        res = binary_search(self.router_ids, "R99")
        self.assertFalse(res["found"])
        self.assertEqual(res["index"], -1)
        self.assertGreater(res["comparisons"], 0)

    def test_binary_search_empty(self):
        res = binary_search([], "R1")
        self.assertFalse(res["found"])
        self.assertEqual(res["index"], -1)
        self.assertEqual(res["comparisons"], 0)

    def test_binary_search_unsorted_rejection(self):
        # Passing an unsorted list should be rejected with an informative error
        res = binary_search(self.unsorted_ids, "R2", verify_sorted=True)
        self.assertFalse(res["found"])
        self.assertIn("error", res)
        self.assertIn("not sorted", res["error"])

    # -------------------------------------------------------------
    # Bubble Sort Tests
    # -------------------------------------------------------------
    def test_bubble_sort_correctness(self):
        res = bubble_sort(self.unsorted_ids)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["sorted_data"], sorted(self.unsorted_ids))
        self.assertEqual(res["input_size"], len(self.unsorted_ids))
        self.assertGreater(res["comparisons"], 0)
        self.assertGreater(res["swaps"], 0)

    def test_bubble_sort_already_sorted(self):
        # Early-exit optimization should terminate in 1 pass
        res = bubble_sort(self.router_ids)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["swaps"], 0)
        self.assertEqual(res["passes"], 1)

    def test_bubble_sort_empty_and_single(self):
        empty_res = bubble_sort([])
        self.assertTrue(empty_res["is_correct"])
        self.assertEqual(empty_res["comparisons"], 0)

        single_res = bubble_sort(["R1"])
        self.assertTrue(single_res["is_correct"])
        self.assertEqual(single_res["comparisons"], 0)

    # -------------------------------------------------------------
    # Insertion Sort Tests
    # -------------------------------------------------------------
    def test_insertion_sort_correctness(self):
        res = insertion_sort(self.unsorted_ids)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["sorted_data"], sorted(self.unsorted_ids))
        self.assertEqual(res["input_size"], len(self.unsorted_ids))
        self.assertGreater(res["comparisons"], 0)
        self.assertGreater(res["shifts"], 0)

    def test_insertion_sort_already_sorted(self):
        res = insertion_sort(self.router_ids)
        self.assertTrue(res["is_correct"])
        self.assertEqual(res["shifts"], 0)
        self.assertEqual(res["comparisons"], len(self.router_ids) - 1)

    def test_insertion_sort_empty_and_single(self):
        empty_res = insertion_sort([])
        self.assertTrue(empty_res["is_correct"])
        self.assertEqual(empty_res["comparisons"], 0)

        single_res = insertion_sort(["R1"])
        self.assertTrue(single_res["is_correct"])
        self.assertEqual(single_res["comparisons"], 0)


if __name__ == "__main__":
    unittest.main()
