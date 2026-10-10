"""
Binary Min-Heap and Max-Heap implementations with sift-up/sift-down operations,
array & tree dual visualization, and Priority Queue features.
"""
from typing import List, Optional, Any, Tuple
from models.simulation import SimulationStep, SimulationResult


class MinHeap:
    """Binary Min-Heap data structure."""

    def __init__(self):
        self.heap: List[int] = []

    def get_parent_idx(self, i: int) -> int:
        return (i - 1) // 2

    def get_left_idx(self, i: int) -> int:
        return 2 * i + 1

    def get_right_idx(self, i: int) -> int:
        return 2 * i + 2

    def peek(self) -> Optional[int]:
        return self.heap[0] if self.heap else None

    def insert(self, val: int) -> SimulationResult:
        """Insert value into Min-Heap and sift up."""
        steps: List[SimulationStep] = []
        self.heap.append(val)
        idx = len(self.heap) - 1

        steps.append(SimulationStep(
            step_type="push",
            current_element=val,
            data_structure_state=list(self.heap),
            highlight_indices=[idx],
            message=f"Appended value {val} at leaf position (index {idx})."
        ))

        swaps = 0
        while idx > 0:
            parent_idx = self.get_parent_idx(idx)
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(self.heap),
                highlight_indices=[idx, parent_idx],
                message=f"Comparing node {self.heap[idx]} (idx {idx}) with parent {self.heap[parent_idx]} (idx {parent_idx})."
            ))

            if self.heap[idx] < self.heap[parent_idx]:
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                swaps += 1
                idx = parent_idx
                steps.append(SimulationStep(
                    step_type="sift_up",
                    data_structure_state=list(self.heap),
                    highlight_indices=[idx],
                    message=f"Sifted up: swapped element into index {idx}."
                ))
            else:
                break

        return SimulationResult(
            algorithm_name="Min-Heap Insert",
            success=True,
            total_steps=len(steps),
            total_swaps=swaps,
            steps=steps,
            message=f"Inserted {val} into Min-Heap."
        )

    def extract_min(self) -> Tuple[Optional[int], SimulationResult]:
        """Extract minimum element from Min-Heap and sift down."""
        steps: List[SimulationStep] = []

        if not self.heap:
            return None, SimulationResult(
                algorithm_name="Min-Heap Extract",
                success=False,
                message="Min-Heap is empty."
            )

        min_val = self.heap[0]
        last_val = self.heap.pop()

        if not self.heap:
            steps.append(SimulationStep(
                step_type="extract",
                current_element=min_val,
                data_structure_state=[],
                message=f"Extracted minimum {min_val}. Heap is now empty."
            ))
            return min_val, SimulationResult(
                algorithm_name="Min-Heap Extract",
                success=True,
                steps=steps,
                message=f"Extracted minimum {min_val}."
            )

        self.heap[0] = last_val
        steps.append(SimulationStep(
            step_type="replace_root",
            current_element=last_val,
            data_structure_state=list(self.heap),
            highlight_indices=[0],
            message=f"Replaced root with last element {last_val}."
        ))

        # Sift down
        idx = 0
        swaps = 0
        n = len(self.heap)

        while True:
            left = self.get_left_idx(idx)
            right = self.get_right_idx(idx)
            smallest = idx

            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                swaps += 1
                idx = smallest
                steps.append(SimulationStep(
                    step_type="sift_down",
                    data_structure_state=list(self.heap),
                    highlight_indices=[idx],
                    message=f"Sifted down to index {idx}."
                ))
            else:
                break

        return min_val, SimulationResult(
            algorithm_name="Min-Heap Extract",
            success=True,
            total_steps=len(steps),
            total_swaps=swaps,
            steps=steps,
            message=f"Extracted min value {min_val}."
        )

    def build_heap(self, arr: List[int]):
        """Build heap from an arbitrary array."""
        self.heap = list(arr)
        n = len(self.heap)
        for i in range(n // 2 - 1, -1, -1):
            idx = i
            while True:
                left = self.get_left_idx(idx)
                right = self.get_right_idx(idx)
                smallest = idx
                if left < n and self.heap[left] < self.heap[smallest]:
                    smallest = left
                if right < n and self.heap[right] < self.heap[smallest]:
                    smallest = right
                if smallest != idx:
                    self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                    idx = smallest
                else:
                    break


class MaxHeap:
    """Binary Max-Heap data structure."""

    def __init__(self):
        self.heap: List[int] = []

    def get_parent_idx(self, i: int) -> int:
        return (i - 1) // 2

    def get_left_idx(self, i: int) -> int:
        return 2 * i + 1

    def get_right_idx(self, i: int) -> int:
        return 2 * i + 2

    def peek(self) -> Optional[int]:
        return self.heap[0] if self.heap else None

    def insert(self, val: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        self.heap.append(val)
        idx = len(self.heap) - 1

        steps.append(SimulationStep(
            step_type="push",
            current_element=val,
            data_structure_state=list(self.heap),
            highlight_indices=[idx],
            message=f"Appended {val} to Max-Heap at index {idx}."
        ))

        swaps = 0
        while idx > 0:
            parent_idx = self.get_parent_idx(idx)
            if self.heap[idx] > self.heap[parent_idx]:
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                swaps += 1
                idx = parent_idx
                steps.append(SimulationStep(
                    step_type="sift_up",
                    data_structure_state=list(self.heap),
                    highlight_indices=[idx],
                    message=f"Sifted up {val} to index {idx}."
                ))
            else:
                break

        return SimulationResult(
            algorithm_name="Max-Heap Insert",
            success=True,
            total_steps=len(steps),
            total_swaps=swaps,
            steps=steps,
            message=f"Inserted {val} into Max-Heap."
        )

    def extract_max(self) -> Tuple[Optional[int], SimulationResult]:
        steps: List[SimulationStep] = []
        if not self.heap:
            return None, SimulationResult(algorithm_name="Max-Heap Extract", success=False, message="Heap empty.")

        max_val = self.heap[0]
        last_val = self.heap.pop()

        if not self.heap:
            return max_val, SimulationResult(algorithm_name="Max-Heap Extract", success=True, message=f"Extracted {max_val}.")

        self.heap[0] = last_val
        idx = 0
        n = len(self.heap)

        while True:
            left = self.get_left_idx(idx)
            right = self.get_right_idx(idx)
            largest = idx

            if left < n and self.heap[left] > self.heap[largest]:
                largest = left
            if right < n and self.heap[right] > self.heap[largest]:
                largest = right

            if largest != idx:
                self.heap[idx], self.heap[largest] = self.heap[largest], self.heap[idx]
                idx = largest
            else:
                break

        return max_val, SimulationResult(algorithm_name="Max-Heap Extract", success=True, message=f"Extracted max {max_val}.")

    def build_heap(self, arr: List[int]):
        self.heap = list(arr)
        n = len(self.heap)
        for i in range(n // 2 - 1, -1, -1):
            idx = i
            while True:
                left = self.get_left_idx(idx)
                right = self.get_right_idx(idx)
                largest = idx
                if left < n and self.heap[left] > self.heap[largest]:
                    largest = left
                if right < n and self.heap[right] > self.heap[largest]:
                    largest = right
                if largest != idx:
                    self.heap[idx], self.heap[largest] = self.heap[largest], self.heap[idx]
                    idx = largest
                else:
                    break
