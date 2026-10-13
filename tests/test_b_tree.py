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

    def test_b_tree_deletion(self):
        tree = BTree(t=2)
        keys = [10, 20, 30, 40, 50, 60, 70]
        for k in keys:
            tree.insert(k)

        # Delete key 30 (internal / leaf node)
        res_del = tree.delete(30)
        self.assertTrue(res_del.success)
        self.assertFalse(tree.search(30).success)

        # Delete missing key returns success=False
        self.assertFalse(tree.delete(999).success)

    def test_empty_b_tree(self):
        tree = BTree(t=2)
        self.assertFalse(tree.search(10).success)
        self.assertFalse(tree.delete(10).success)


if __name__ == "__main__":
    unittest.main()
