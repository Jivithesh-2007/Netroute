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

        # Missing search and delete
        self.assertFalse(table.search(999).success)
        self.assertFalse(table.delete(999).success)

        table.clear()
        self.assertEqual(table.item_count, 0)

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

    def test_linear_probing_full_table(self):
        """Test full table behavior for linear probing."""
        table = HashTableLinearProbing(size=3)
        self.assertTrue(table.insert(1).success)
        self.assertTrue(table.insert(2).success)
        self.assertTrue(table.insert(3).success)
        
        # 4th insert into size 3 table fails cleanly
        res_full = table.insert(4)
        self.assertFalse(res_full.success)
        self.assertIn("full", res_full.message.lower())

    def test_linear_probing_delete_miss(self):
        table = HashTableLinearProbing(size=5)
        table.insert(10)
        self.assertFalse(table.delete(999).success)


if __name__ == "__main__":
    unittest.main()
