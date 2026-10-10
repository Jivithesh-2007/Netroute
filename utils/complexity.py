"""
Theoretical time and space complexity lookup table and explanations.
"""
from typing import Dict, Any

COMPLEXITY_DATA: Dict[str, Dict[str, str]] = {
    "BFS Routing": {
        "time_best": "O(V + E)",
        "time_avg": "O(V + E)",
        "time_worst": "O(V + E)",
        "space": "O(V)",
        "description": "Breadth-First Search queue traversal guarantees shortest path in unweighted graphs."
    },
    "DFS Routing": {
        "time_best": "O(V + E)",
        "time_avg": "O(V + E)",
        "time_worst": "O(V + E)",
        "space": "O(V)",
        "description": "Depth-First Search stack traversal explores deep paths first; path is valid but not necessarily shortest."
    },
    "Linear Search": {
        "time_best": "O(1)",
        "time_avg": "O(N)",
        "time_worst": "O(N)",
        "space": "O(1)",
        "description": "Sequential search through elements one by one."
    },
    "Binary Search": {
        "time_best": "O(1)",
        "time_avg": "O(log N)",
        "time_worst": "O(log N)",
        "space": "O(1) [Iterative] / O(log N) [Recursive]",
        "description": "Divide-and-conquer search on sorted array by halving search interval."
    },
    "Interpolation Search": {
        "time_best": "O(1)",
        "time_avg": "O(log log N)",
        "time_worst": "O(N)",
        "space": "O(1)",
        "description": "Probes near estimated target position for uniformly distributed sorted values."
    },
    "Bubble Sort": {
        "time_best": "O(N)",
        "time_avg": "O(N²)",
        "time_worst": "O(N²)",
        "space": "O(1)",
        "description": "Repeatedly swaps adjacent out-of-order elements until sorted."
    },
    "Insertion Sort": {
        "time_best": "O(N)",
        "time_avg": "O(N²)",
        "time_worst": "O(N²)",
        "space": "O(1)",
        "description": "Builds final sorted array one item at a time by shifting."
    },
    "Selection Sort": {
        "time_best": "O(N²)",
        "time_avg": "O(N²)",
        "time_worst": "O(N²)",
        "space": "O(1)",
        "description": "Finds minimum element from unsorted portion and swaps into position."
    },
    "Merge Sort": {
        "time_best": "O(N log N)",
        "time_avg": "O(N log N)",
        "time_worst": "O(N log N)",
        "space": "O(N)",
        "description": "Divide-and-conquer algorithm splitting array into halves and merging sorted halves."
    },
    "Separate Chaining": {
        "time_best": "O(1)",
        "time_avg": "O(1 + alpha)",
        "time_worst": "O(N)",
        "space": "O(M + N)",
        "description": "Collisions resolved via linked list buckets. Performance degrades gracefully with load factor."
    },
    "Linear Probing": {
        "time_best": "O(1)",
        "time_avg": "O(1)",
        "time_worst": "O(N)",
        "space": "O(M)",
        "description": "Open addressing probing sequentially. Prone to primary clustering."
    },
    "BST": {
        "time_best": "O(log N)",
        "time_avg": "O(log N)",
        "time_worst": "O(N) [Skewed]",
        "space": "O(N)",
        "description": "Unbalanced binary search tree. Can degenerate into linked list."
    },
    "AVL Tree": {
        "time_best": "O(log N)",
        "time_avg": "O(log N)",
        "time_worst": "O(log N)",
        "space": "O(N)",
        "description": "Strictly height-balanced BST guaranteeing O(log N) lookup, insertion, and deletion."
    },
    "Binary Heap": {
        "time_best": "O(1) [Peek]",
        "time_avg": "O(log N) [Insert/Extract]",
        "time_worst": "O(log N)",
        "space": "O(N)",
        "description": "Complete binary tree satisfying min-heap or max-heap property."
    },
    "B-Tree": {
        "time_best": "O(log N)",
        "time_avg": "O(log N)",
        "time_worst": "O(log N)",
        "space": "O(N)",
        "description": "Self-balancing multi-way search tree optimized for systems and storage."
    }
}


def get_complexity_info(algorithm_name: str) -> Dict[str, str]:
    """Return complexity info dict or default fallback."""
    return COMPLEXITY_DATA.get(algorithm_name, {
        "time_best": "N/A",
        "time_avg": "N/A",
        "time_worst": "N/A",
        "space": "N/A",
        "description": "Algorithm complexity specification."
    })
