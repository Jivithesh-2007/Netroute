"""
Unit tests for Binary Search Tree operations (Insert, Search, 3-case Delete).
"""
import unittest
from algorithms.binary_search_tree import BinarySearchTree
from algorithms.tree_traversals import inorder_traversal


class TestBST(unittest.TestCase):

    def test_bst_operations(self):
        bst = BinarySearchTree()
        keys = [50, 30, 70, 20, 40, 60, 80]
        for k in keys:
            bst.insert(k)

        # Inorder should return sorted array
        seq, _ = inorder_traversal(bst.root)
        self.assertEqual(seq, sorted(keys))

        # Search
        self.assertTrue(bst.search(40).success)
        self.assertFalse(bst.search(99).success)

        # Min and Max
        self.assertEqual(bst.find_min(), 20)
        self.assertEqual(bst.find_max(), 80)

        # Duplicate insertion rejected
        self.assertFalse(bst.insert(50).success)

        # Case 1: Delete Leaf Node (20)
        self.assertTrue(bst.delete(20).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(20, seq)

        # Case 2: Delete 1-Child Node
        bst.insert(25)  # 30 now has left child 25
        self.assertTrue(bst.delete(30).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(30, seq)
        self.assertIn(25, seq)

        # Case 3: Delete 2-Children Node (50 - root)
        self.assertTrue(bst.delete(50).success)
        seq, _ = inorder_traversal(bst.root)
        self.assertNotIn(50, seq)

        # Delete non-existent key
        self.assertFalse(bst.delete(999).success)

        # Clear BST
        bst.clear()
        self.assertIsNone(bst.root)


if __name__ == "__main__":
    unittest.main()
