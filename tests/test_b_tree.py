"""
Unit tests for B-Tree multi-key node splitting and search.
"""
import unittest
from algorithms.b_tree import BTree


class TestBTree(unittest.TestCase):

    def test_b_tree_insert_search(self):
        tree = BTree(t=2)  # Max 3 keys per node before splitting
        keys = [10, 20, 30, 40, 50, 60, 70]
        for k in keys:
            tree.insert(k)

        for k in keys:
            self.assertTrue(tree.search(k).success)

        self.assertFalse(tree.search(999).success)


if __name__ == "__main__":
    unittest.main()
