"""
Unit tests for searching algorithms (Linear, Binary Iterative/Recursive, Interpolation).
"""
import unittest
from algorithms.searching import (
    linear_search, binary_search_iterative, binary_search_recursive, interpolation_search
)


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
        """Test interpolation search handles duplicate range values without zero division."""
        res = interpolation_search(self.duplicates_arr, 20)
        self.assertTrue(res.success)

    def test_negative_values(self):
        res = binary_search_iterative(self.negative_arr, -20)
        self.assertTrue(res.success)
        self.assertEqual(self.negative_arr[res.path[0]], -20)


if __name__ == "__main__":
    unittest.main()
