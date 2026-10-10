"""
Unit tests for sorting algorithms (Bubble, Insertion, Selection, Merge).
"""
import unittest
from algorithms.sorting import bubble_sort, insertion_sort, selection_sort, merge_sort


class TestSorting(unittest.TestCase):

    def setUp(self):
        self.unsorted = [64, 34, 25, 12, 22, 11, 90]
        self.expected = [11, 12, 22, 25, 34, 64, 90]
        self.already_sorted = [1, 2, 3, 4, 5]
        self.reverse_sorted = [5, 4, 3, 2, 1]

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

    def test_already_sorted_input(self):
        self.assertEqual(bubble_sort(self.already_sorted).path, self.already_sorted)
        self.assertEqual(insertion_sort(self.already_sorted).path, self.already_sorted)

    def test_reverse_sorted_input(self):
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(merge_sort(self.reverse_sorted).path, expected)


if __name__ == "__main__":
    unittest.main()
