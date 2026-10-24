"""Module 3: algorithms.py - Searching, Sorting, and Hash Table (Chaining)."""

def linear_search(arr, target):
    """Linear Search: Compares target element by element."""
    steps = 0
    for i in range(len(arr)):
        steps += 1
        if arr[i] == target:
            return i, steps
    return -1, steps

def binary_search(arr, target):
    """Binary Search: Searches target in sorted array by halving."""
    steps = 0
    low, high = 0, len(arr) - 1
    while low <= high:
        steps += 1
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid, steps
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, steps

def bubble_sort(arr):
    """Bubble Sort: Repeatedly swaps adjacent out-of-order elements."""
    a = list(arr)
    n, steps = len(a), 0
    for i in range(n):
        for j in range(0, n - i - 1):
            steps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a, steps

def selection_sort(arr):
    """Selection Sort: Selects smallest element and places it in front."""
    a = list(arr)
    n, steps = len(a), 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            steps += 1
            if a[j] < a[min_idx]:
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a, steps

def insertion_sort(arr):
    """Insertion Sort: Shifts elements to insert current key in order."""
    a = list(arr)
    n, steps = len(a), 0
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            steps += 1
            a[j + 1] = a[j]
            j -= 1
        if j >= 0:
            steps += 1
        a[j + 1] = key
    return a, steps

class HashTable:
    """Hash Table using Separate Chaining for collision handling."""
    def __init__(self, size=7):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def insert(self, key):
        idx = key % self.size
        if key not in self.buckets[idx]:
            self.buckets[idx].append(key)
            return True, f"Key {key} inserted at index {idx}."
        return False, f"Key {key} already exists at index {idx}."

    def search(self, key):
        idx = key % self.size
        if key in self.buckets[idx]:
            return True, f"Found {key} at index {idx}."
        return False, f"Key {key} not found."

    def delete(self, key):
        idx = key % self.size
        if key in self.buckets[idx]:
            self.buckets[idx].remove(key)
            return True, f"Deleted {key} from index {idx}."
        return False, f"Key {key} not present to delete."
