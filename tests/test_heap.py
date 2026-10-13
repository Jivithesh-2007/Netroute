"""
Unit tests for Min-Heap and Max-Heap priority queue operations.
"""
import unittest
from algorithms.heap import MinHeap, MaxHeap


class TestHeap(unittest.TestCase):

    def test_min_heap(self):
        heap = MinHeap()
        for v in [50, 20, 40, 10, 30]:
            heap.insert(v)

        self.assertEqual(heap.peek(), 10)

        extracted = []
        while heap.heap:
            val, _ = heap.extract_min()
            extracted.append(val)

        self.assertEqual(extracted, [10, 20, 30, 40, 50])

    def test_empty_heap(self):
        heap = MinHeap()
        self.assertIsNone(heap.peek())
        val, res = heap.extract_min()
        self.assertIsNone(val)
        self.assertFalse(res.success)

    def test_build_heap(self):
        heap = MinHeap()
        heap.build_heap([90, 40, 10, 30, 20])
        self.assertEqual(heap.peek(), 10)

    def test_max_heap(self):
        heap = MaxHeap()
        for v in [50, 20, 40, 10, 30]:
            heap.insert(v)

        self.assertEqual(heap.peek(), 50)
        val, res = heap.extract_max()
        self.assertEqual(val, 50)


if __name__ == "__main__":
    unittest.main()
