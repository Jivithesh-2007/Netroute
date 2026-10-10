"""
Unit tests for Hash Table collision strategies (Separate Chaining and Linear Probing).
"""
import unittest
from algorithms.hashing import HashTableChaining, HashTableLinearProbing


class TestHashing(unittest.TestCase):

    def test_separate_chaining(self):
        table = HashTableChaining(size=5)
        table.insert(10)  # hash 0
        table.insert(15)  # hash 0 collision

        res = table.search(15)
        self.assertTrue(res.success)
        self.assertEqual(table.collisions, 1)

        del_res = table.delete(10)
        self.assertTrue(del_res.success)

        res_after = table.search(15)
        self.assertTrue(res_after.success)

    def test_linear_probing_tombstones(self):
        """Test linear probing maintains search chain after deletion using tombstones."""
        table = HashTableLinearProbing(size=5)
        table.insert(10)  # index 0
        table.insert(15)  # index 1 (probed)
        table.insert(20)  # index 2 (probed)

        # Delete middle element (15)
        table.delete(15)
        self.assertEqual(table.table[1], table.DELETED)

        # Searching for 20 must skip DELETED tombstone and succeed
        res = table.search(20)
        self.assertTrue(res.success)
        self.assertEqual(res.path[0], 2)


if __name__ == "__main__":
    unittest.main()
