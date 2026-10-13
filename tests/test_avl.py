"""
Unit tests for self-balancing AVL Tree and rotation cases.
"""
import unittest
from algorithms.avl_tree import AVLTree
from algorithms.tree_traversals import inorder_traversal, get_tree_metrics


class TestAVL(unittest.TestCase):

    def test_avl_rotations_and_balance(self):
        avl = AVLTree()
        # Sequential insert triggers rotations
        for k in [10, 20, 30, 40, 50, 25]:
            avl.insert(k)

        # Inorder sequence remains sorted
        seq, _ = inorder_traversal(avl.root)
        self.assertEqual(seq, [10, 20, 25, 30, 40, 50])

        # Height must be strictly balanced O(log N)
        h, total, _ = get_tree_metrics(avl.root)
        self.assertLessEqual(h, 4)
        self.assertEqual(total, 6)

        # All balance factors must be in range [-1, 1]
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

        # Delete key
        self.assertTrue(avl.delete(50).success)
        self.assertFalse(avl.search(50).success)

        # Delete missing key returns success=False
        self.assertFalse(avl.delete(999).success)


if __name__ == "__main__":
    unittest.main()
