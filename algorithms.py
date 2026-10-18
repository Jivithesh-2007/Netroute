import random
import time
from collections import deque
from typing import List, Tuple, Optional, Any, Dict
from network import SimulationStep, SimulationResult


def linear_search(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Linear Search",
            success=False,
            total_steps=0,
            total_comparisons=0,
            message="Input array is empty."
        )

    for i, val in enumerate(arr):
        comparisons += 1
        steps.append(SimulationStep(
            step_type="compare",
            current_element=val,
            data_structure_state=list(arr),
            highlight_indices=[i],
            message=f"Index {i}: Comparing value {val} with target {target}."
        ))

        if val == target:
            steps.append(SimulationStep(
                step_type="found",
                current_element=val,
                data_structure_state=list(arr),
                highlight_indices=[i],
                message=f"Target {target} found at index {i}!"
            ))
            exec_time = (time.perf_counter() - start_time) * 1000
            return SimulationResult(
                algorithm_name="Linear Search",
                success=True,
                path=[i],
                total_steps=len(steps),
                total_comparisons=comparisons,
                execution_time_ms=exec_time,
                steps=steps,
                message=f"Found target {target} at index {i} after {comparisons} comparisons."
            )

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="not_found",
        data_structure_state=list(arr),
        message=f"Target {target} not present in array."
    ))

    return SimulationResult(
        algorithm_name="Linear Search",
        success=False,
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Target {target} not found after {comparisons} comparisons."
    )


def binary_search_iterative(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Binary Search (Iterative)",
            success=False,
            total_steps=0,
            total_comparisons=0,
            message="Input array is empty."
        )

    if arr != sorted(arr):
        return SimulationResult(
            algorithm_name="Binary Search (Iterative)",
            success=False,
            message="Binary search requires a sorted array."
        )

    low, high = 0, len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_val = arr[mid]

        steps.append(SimulationStep(
            step_type="probe",
            current_element=mid_val,
            data_structure_state=list(arr),
            highlight_indices=[mid],
            secondary_indices=[low, high],
            message=f"Search range [{low}..{high}]: Probing mid index {mid} (val = {mid_val})."
        ))

        if mid_val == target:
            steps.append(SimulationStep(
                step_type="found",
                current_element=mid_val,
                data_structure_state=list(arr),
                highlight_indices=[mid],
                message=f"Target {target} found at index {mid}!"
            ))
            exec_time = (time.perf_counter() - start_time) * 1000
            return SimulationResult(
                algorithm_name="Binary Search (Iterative)",
                success=True,
                path=[mid],
                total_steps=len(steps),
                total_comparisons=comparisons,
                execution_time_ms=exec_time,
                steps=steps,
                message=f"Found target {target} at index {mid} in {comparisons} comparisons."
            )

        if mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="not_found",
        data_structure_state=list(arr),
        message=f"Target {target} not present in array."
    ))

    return SimulationResult(
        algorithm_name="Binary Search (Iterative)",
        success=False,
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Target {target} not found after {comparisons} comparisons."
    )


def binary_search_recursive(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = [0]

    if not arr:
        return SimulationResult(
            algorithm_name="Binary Search (Recursive)",
            success=False,
            total_steps=0,
            total_comparisons=0,
            message="Input array is empty."
        )

    if arr != sorted(arr):
        return SimulationResult(
            algorithm_name="Binary Search (Recursive)",
            success=False,
            message="Binary search requires a sorted array."
        )

    def _rec_search(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = (low + high) // 2
        comparisons[0] += 1
        mid_val = arr[mid]

        steps.append(SimulationStep(
            step_type="probe",
            current_element=mid_val,
            data_structure_state=list(arr),
            highlight_indices=[mid],
            secondary_indices=[low, high],
            message=f"Rec level range [{low}..{high}]: Probing mid index {mid} (val = {mid_val})."
        ))

        if mid_val == target:
            return mid
        elif mid_val < target:
            return _rec_search(mid + 1, high)
        else:
            return _rec_search(low, mid - 1)

    res_idx = _rec_search(0, len(arr) - 1)
    exec_time = (time.perf_counter() - start_time) * 1000

    if res_idx != -1:
        steps.append(SimulationStep(
            step_type="found",
            current_element=arr[res_idx],
            data_structure_state=list(arr),
            highlight_indices=[res_idx],
            message=f"Recursive search found target {target} at index {res_idx}."
        ))
        return SimulationResult(
            algorithm_name="Binary Search (Recursive)",
            success=True,
            path=[res_idx],
            total_steps=len(steps),
            total_comparisons=comparisons[0],
            execution_time_ms=exec_time,
            steps=steps,
            message=f"Found target {target} at index {res_idx} recursively."
        )
    else:
        steps.append(SimulationStep(
            step_type="not_found",
            data_structure_state=list(arr),
            message=f"Target {target} not found in array."
        ))
        return SimulationResult(
            algorithm_name="Binary Search (Recursive)",
            success=False,
            total_steps=len(steps),
            total_comparisons=comparisons[0],
            execution_time_ms=exec_time,
            steps=steps,
            message=f"Target {target} not found recursively."
        )


def interpolation_search(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Interpolation Search",
            success=False,
            total_steps=0,
            total_comparisons=0,
            message="Input array is empty."
        )

    if arr != sorted(arr):
        return SimulationResult(
            algorithm_name="Interpolation Search",
            success=False,
            message="Interpolation search requires a sorted array."
        )

    low, high = 0, len(arr) - 1

    while low <= high and target >= arr[low] and target <= arr[high]:
        comparisons += 1
        if arr[low] == arr[high]:
            if arr[low] == target:
                steps.append(SimulationStep(
                    step_type="found",
                    current_element=arr[low],
                    data_structure_state=list(arr),
                    highlight_indices=[low],
                    message=f"Target {target} found at index {low} (endpoint match)."
                ))
                exec_time = (time.perf_counter() - start_time) * 1000
                return SimulationResult(
                    algorithm_name="Interpolation Search",
                    success=True,
                    path=[low],
                    total_steps=len(steps),
                    total_comparisons=comparisons,
                    execution_time_ms=exec_time,
                    steps=steps,
                    message=f"Found target {target} at index {low}."
                )
            break

        pos = low + int(((target - arr[low]) * (high - low)) / (arr[high] - arr[low]))
        pos = max(low, min(high, pos))

        probe_val = arr[pos]
        steps.append(SimulationStep(
            step_type="probe",
            current_element=probe_val,
            data_structure_state=list(arr),
            highlight_indices=[pos],
            secondary_indices=[low, high],
            message=f"Interpolated pos {pos} for range [{low}..{high}] with val = {probe_val}."
        ))

        if probe_val == target:
            steps.append(SimulationStep(
                step_type="found",
                current_element=probe_val,
                data_structure_state=list(arr),
                highlight_indices=[pos],
                message=f"Target {target} found at index {pos}!"
            ))
            exec_time = (time.perf_counter() - start_time) * 1000
            return SimulationResult(
                algorithm_name="Interpolation Search",
                success=True,
                path=[pos],
                total_steps=len(steps),
                total_comparisons=comparisons,
                execution_time_ms=exec_time,
                steps=steps,
                message=f"Found target {target} at index {pos}."
            )

        if probe_val < target:
            low = pos + 1
        else:
            high = pos - 1

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="not_found",
        data_structure_state=list(arr),
        message=f"Target {target} not present in array."
    ))

    return SimulationResult(
        algorithm_name="Interpolation Search",
        success=False,
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Target {target} not found."
    )


def bubble_sort(arr_input: List[int]) -> SimulationResult:
    arr = list(arr_input)
    n = len(arr)
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    swaps = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Bubble Sort",
            success=True,
            path=[],
            total_steps=0,
            message="Empty array."
        )

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(arr),
        message="Initial unsorted array."
    ))

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(arr),
                highlight_indices=[j, j + 1],
                message=f"Comparing arr[{j}] ({arr[j]}) and arr[{j+1}] ({arr[j+1]})."
            ))

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
                steps.append(SimulationStep(
                    step_type="swap",
                    data_structure_state=list(arr),
                    highlight_indices=[j, j + 1],
                    message=f"Swapped elements to [{arr[j]}, {arr[j+1]}]."
                ))

        if not swapped:
            break

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="sorted",
        data_structure_state=list(arr),
        message="Array successfully sorted with Bubble Sort."
    ))

    return SimulationResult(
        algorithm_name="Bubble Sort",
        success=True,
        path=list(arr),
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=swaps,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Bubble Sort completed with {comparisons} comparisons and {swaps} swaps."
    )


def insertion_sort(arr_input: List[int]) -> SimulationResult:
    arr = list(arr_input)
    n = len(arr)
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    swaps = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Insertion Sort",
            success=True,
            path=[],
            total_steps=0,
            message="Empty array."
        )

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(arr),
        message="Initial array for Insertion Sort."
    ))

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        steps.append(SimulationStep(
            step_type="select",
            data_structure_state=list(arr),
            highlight_indices=[i],
            message=f"Selected key arr[{i}] = {key} to insert into sorted sub-array."
        ))

        while j >= 0:
            comparisons += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(arr),
                highlight_indices=[j, j + 1],
                message=f"Comparing key {key} with arr[{j}] = {arr[j]}."
            ))
            if arr[j] > key:
                arr[j + 1] = arr[j]
                swaps += 1
                j -= 1
                steps.append(SimulationStep(
                    step_type="shift",
                    data_structure_state=list(arr),
                    highlight_indices=[j + 1],
                    message=f"Shifted element {arr[j+1]} right."
                ))
            else:
                break
        arr[j + 1] = key
        steps.append(SimulationStep(
            step_type="insert",
            data_structure_state=list(arr),
            highlight_indices=[j + 1],
            message=f"Inserted key {key} at position {j+1}."
        ))

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="sorted",
        data_structure_state=list(arr),
        message="Array successfully sorted with Insertion Sort."
    ))

    return SimulationResult(
        algorithm_name="Insertion Sort",
        success=True,
        path=list(arr),
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=swaps,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Insertion Sort completed with {comparisons} comparisons and {swaps} shifts."
    )


def selection_sort(arr_input: List[int]) -> SimulationResult:
    arr = list(arr_input)
    n = len(arr)
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    swaps = 0

    if not arr:
        return SimulationResult(
            algorithm_name="Selection Sort",
            success=True,
            path=[],
            total_steps=0,
            message="Empty array."
        )

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(arr),
        message="Initial array for Selection Sort."
    ))

    for i in range(n):
        min_idx = i
        steps.append(SimulationStep(
            step_type="select_min",
            data_structure_state=list(arr),
            highlight_indices=[i],
            message=f"Pass {i+1}: Assuming min at index {i} ({arr[i]})."
        ))

        for j in range(i + 1, n):
            comparisons += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(arr),
                highlight_indices=[j],
                secondary_indices=[min_idx],
                message=f"Comparing arr[{j}] ({arr[j]}) with current min ({arr[min_idx]})."
            ))
            if arr[j] < arr[min_idx]:
                min_idx = j
                steps.append(SimulationStep(
                    step_type="new_min",
                    data_structure_state=list(arr),
                    highlight_indices=[min_idx],
                    message=f"New minimum found at index {min_idx} ({arr[min_idx]})."
                ))

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
            steps.append(SimulationStep(
                step_type="swap",
                data_structure_state=list(arr),
                highlight_indices=[i, min_idx],
                message=f"Swapped minimum element {arr[i]} into index {i}."
            ))

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="sorted",
        data_structure_state=list(arr),
        message="Array successfully sorted with Selection Sort."
    ))

    return SimulationResult(
        algorithm_name="Selection Sort",
        success=True,
        path=list(arr),
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=swaps,
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Selection Sort completed with {comparisons} comparisons and {swaps} swaps."
    )


def merge_sort(arr_input: List[int]) -> SimulationResult:
    arr = list(arr_input)
    n = len(arr)
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = [0]
    writes = [0]

    if not arr:
        return SimulationResult(
            algorithm_name="Merge Sort",
            success=True,
            path=[],
            total_steps=0,
            message="Empty array."
        )

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(arr),
        message="Initial array for Merge Sort."
    ))

    def _merge_sort(l: int, r: int):
        if l < r:
            m = (l + r) // 2
            _merge_sort(l, m)
            _merge_sort(m + 1, r)
            _merge(l, m, r)

    def _merge(l: int, m: int, r: int):
        left_sub = arr[l:m + 1]
        right_sub = arr[m + 1:r + 1]

        i = j = 0
        k = l

        steps.append(SimulationStep(
            step_type="divide",
            data_structure_state=list(arr),
            secondary_indices=list(range(l, r + 1)),
            message=f"Merging sub-arrays [{l}..{m}] and [{m+1}..{r}]."
        ))

        while i < len(left_sub) and j < len(right_sub):
            comparisons[0] += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(arr),
                highlight_indices=[l + i, m + 1 + j],
                message=f"Comparing left element {left_sub[i]} with right element {right_sub[j]}."
            ))
            if left_sub[i] <= right_sub[j]:
                arr[k] = left_sub[i]
                i += 1
            else:
                arr[k] = right_sub[j]
                j += 1
            writes[0] += 1
            steps.append(SimulationStep(
                step_type="write",
                data_structure_state=list(arr),
                highlight_indices=[k],
                message=f"Placed value {arr[k]} into index {k}."
            ))
            k += 1

        while i < len(left_sub):
            arr[k] = left_sub[i]
            i += 1
            k += 1
            writes[0] += 1
            steps.append(SimulationStep(
                step_type="write",
                data_structure_state=list(arr),
                highlight_indices=[k - 1],
                message=f"Placed remaining left element {arr[k-1]} at index {k-1}."
            ))

        while j < len(right_sub):
            arr[k] = right_sub[j]
            j += 1
            k += 1
            writes[0] += 1
            steps.append(SimulationStep(
                step_type="write",
                data_structure_state=list(arr),
                highlight_indices=[k - 1],
                message=f"Placed remaining right element {arr[k-1]} at index {k-1}."
            ))

    _merge_sort(0, n - 1)

    exec_time = (time.perf_counter() - start_time) * 1000
    steps.append(SimulationStep(
        step_type="sorted",
        data_structure_state=list(arr),
        message="Array successfully sorted with Merge Sort."
    ))

    return SimulationResult(
        algorithm_name="Merge Sort",
        success=True,
        path=list(arr),
        total_steps=len(steps),
        total_comparisons=comparisons[0],
        total_swaps=writes[0],
        execution_time_ms=exec_time,
        steps=steps,
        message=f"Merge Sort completed with {comparisons[0]} comparisons and {writes[0]} array writes."
    )


class HashTableChaining:
    def __init__(self, size: int = 10):
        self.size = size
        self.buckets: List[List[Tuple[int, Any]]] = [[] for _ in range(size)]
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0

    def hash_function(self, key: int) -> int:
        return abs(key) % self.size

    def get_load_factor(self) -> float:
        return self.item_count / float(self.size)

    def insert(self, key: int, value: Any = None) -> SimulationResult:
        steps: List[SimulationStep] = []
        val = value if value is not None else f"Val_{key}"
        index = self.hash_function(key)

        steps.append(SimulationStep(
            step_type="hash",
            highlight_indices=[index],
            message=f"Hashed key {key} -> Bucket index {index} (hash({key}) = {key} % {self.size})."
        ))

        bucket = self.buckets[index]
        if len(bucket) > 0:
            self.collisions += 1

        for i, (k, v) in enumerate(bucket):
            self.total_probes += 1
            steps.append(SimulationStep(
                step_type="probe",
                highlight_indices=[index],
                secondary_indices=[i],
                message=f"Probing bucket {index} slot {i}: key {k}."
            ))
            if k == key:
                bucket[i] = (key, val)
                steps.append(SimulationStep(
                    step_type="update",
                    highlight_indices=[index],
                    message=f"Updated value for existing key {key} in bucket {index}."
                ))
                return SimulationResult(
                    algorithm_name="Separate Chaining Insert",
                    success=True,
                    total_steps=len(steps),
                    steps=steps,
                    message=f"Updated key {key} in bucket {index}."
                )

        bucket.append((key, val))
        self.item_count += 1
        self.total_probes += 1

        steps.append(SimulationStep(
            step_type="insert",
            highlight_indices=[index],
            message=f"Inserted ({key}, {val}) into bucket {index} (bucket chain len: {len(bucket)})."
        ))

        return SimulationResult(
            algorithm_name="Separate Chaining Insert",
            success=True,
            total_steps=len(steps),
            steps=steps,
            message=f"Successfully inserted key {key} into bucket {index}."
        )

    def search(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        index = self.hash_function(key)

        steps.append(SimulationStep(
            step_type="hash",
            highlight_indices=[index],
            message=f"Hashed key {key} -> Bucket index {index}."
        ))

        bucket = self.buckets[index]
        probes = 0
        for i, (k, v) in enumerate(bucket):
            probes += 1
            steps.append(SimulationStep(
                step_type="probe",
                highlight_indices=[index],
                secondary_indices=[i],
                message=f"Probing bucket {index} slot {i} (key={k})."
            ))
            if k == key:
                steps.append(SimulationStep(
                    step_type="found",
                    highlight_indices=[index],
                    message=f"Key {key} found in bucket {index} after {probes} probes!"
                ))
                return SimulationResult(
                    algorithm_name="Separate Chaining Search",
                    success=True,
                    path=[index, i],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Found key {key} in bucket {index} with value '{v}'."
                )

        steps.append(SimulationStep(
            step_type="not_found",
            highlight_indices=[index],
            message=f"Key {key} not found in bucket {index}."
        ))
        return SimulationResult(
            algorithm_name="Separate Chaining Search",
            success=False,
            total_steps=len(steps),
            total_comparisons=probes,
            steps=steps,
            message=f"Key {key} not present in hash table."
        )

    def delete(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        index = self.hash_function(key)

        bucket = self.buckets[index]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.item_count -= 1
                steps.append(SimulationStep(
                    step_type="delete",
                    highlight_indices=[index],
                    message=f"Deleted key {key} from bucket {index}."
                ))
                return SimulationResult(
                    algorithm_name="Separate Chaining Delete",
                    success=True,
                    total_steps=len(steps),
                    steps=steps,
                    message=f"Deleted key {key} from bucket {index}."
                )

        steps.append(SimulationStep(
            step_type="not_found",
            highlight_indices=[index],
            message=f"Key {key} not found for deletion."
        ))
        return SimulationResult(
            algorithm_name="Separate Chaining Delete",
            success=False,
            total_steps=len(steps),
            steps=steps,
            message=f"Key {key} not present."
        )

    def clear(self):
        self.buckets = [[] for _ in range(self.size)]
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0


class HashTableLinearProbing:
    DELETED = "__DELETED__"

    def __init__(self, size: int = 10):
        self.size = size
        self.table: List[Optional[Tuple[int, Any]]] = [None] * size
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0

    def hash_function(self, key: int) -> int:
        return abs(key) % self.size

    def get_load_factor(self) -> float:
        return self.item_count / float(self.size)

    def insert(self, key: int, value: Any = None) -> SimulationResult:
        steps: List[SimulationStep] = []
        val = value if value is not None else f"Val_{key}"

        if self.item_count >= self.size:
            return SimulationResult(
                algorithm_name="Linear Probing Insert",
                success=False,
                message="Hash Table is completely full! Cannot insert."
            )

        initial_idx = self.hash_function(key)
        steps.append(SimulationStep(
            step_type="hash",
            highlight_indices=[initial_idx],
            message=f"Hashed key {key} -> initial index {initial_idx}."
        ))

        probes = 0
        first_deleted_idx = None

        for i in range(self.size):
            idx = (initial_idx + i) % self.size
            probes += 1
            self.total_probes += 1
            cell = self.table[idx]

            steps.append(SimulationStep(
                step_type="probe",
                highlight_indices=[idx],
                message=f"Probe {i+1}: checking table index {idx} (content={cell})."
            ))

            if cell is None:
                insert_idx = first_deleted_idx if first_deleted_idx is not None else idx
                self.table[insert_idx] = (key, val)
                self.item_count += 1
                if i > 0:
                    self.collisions += 1

                steps.append(SimulationStep(
                    step_type="insert",
                    highlight_indices=[insert_idx],
                    message=f"Inserted ({key}, {val}) at index {insert_idx} after {probes} probes."
                ))
                return SimulationResult(
                    algorithm_name="Linear Probing Insert",
                    success=True,
                    path=[insert_idx],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Inserted key {key} at index {insert_idx}."
                )

            elif cell == self.DELETED:
                if first_deleted_idx is None:
                    first_deleted_idx = idx

            elif cell[0] == key:
                self.table[idx] = (key, val)
                steps.append(SimulationStep(
                    step_type="update",
                    highlight_indices=[idx],
                    message=f"Key {key} already exists at index {idx}. Updated value."
                ))
                return SimulationResult(
                    algorithm_name="Linear Probing Insert",
                    success=True,
                    path=[idx],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Updated key {key} at index {idx}."
                )

        if first_deleted_idx is not None:
            self.table[first_deleted_idx] = (key, val)
            self.item_count += 1
            steps.append(SimulationStep(
                step_type="insert",
                highlight_indices=[first_deleted_idx],
                message=f"Inserted ({key}, {val}) into tombstone slot {first_deleted_idx}."
            ))
            return SimulationResult(
                algorithm_name="Linear Probing Insert",
                success=True,
                path=[first_deleted_idx],
                total_steps=len(steps),
                total_comparisons=probes,
                steps=steps,
                message=f"Inserted key {key} into tombstone slot {first_deleted_idx}."
            )

        return SimulationResult(
            algorithm_name="Linear Probing Insert",
            success=False,
            message="No available slot found for insertion."
        )

    def search(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        initial_idx = self.hash_function(key)

        steps.append(SimulationStep(
            step_type="hash",
            highlight_indices=[initial_idx],
            message=f"Hashed key {key} -> initial index {initial_idx}."
        ))

        probes = 0
        for i in range(self.size):
            idx = (initial_idx + i) % self.size
            probes += 1
            cell = self.table[idx]

            steps.append(SimulationStep(
                step_type="probe",
                highlight_indices=[idx],
                message=f"Probe {i+1}: checking table index {idx}."
            ))

            if cell is None:
                steps.append(SimulationStep(
                    step_type="not_found",
                    highlight_indices=[idx],
                    message=f"Hit empty cell at index {idx}. Key {key} does not exist."
                ))
                return SimulationResult(
                    algorithm_name="Linear Probing Search",
                    success=False,
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Key {key} not found after {probes} probes."
                )

            elif cell != self.DELETED and cell[0] == key:
                steps.append(SimulationStep(
                    step_type="found",
                    highlight_indices=[idx],
                    message=f"Found key {key} at table index {idx} after {probes} probes!"
                ))
                return SimulationResult(
                    algorithm_name="Linear Probing Search",
                    success=True,
                    path=[idx],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Key {key} found at index {idx} (val: '{cell[1]}')."
                )

        return SimulationResult(
            algorithm_name="Linear Probing Search",
            success=False,
            total_steps=len(steps),
            total_comparisons=probes,
            steps=steps,
            message=f"Key {key} not found."
        )

    def delete(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        initial_idx = self.hash_function(key)

        probes = 0
        for i in range(self.size):
            idx = (initial_idx + i) % self.size
            probes += 1
            cell = self.table[idx]

            steps.append(SimulationStep(
                step_type="probe",
                highlight_indices=[idx],
                message=f"Probe {i+1}: checking index {idx} for key {key} deletion."
            ))

            if cell is None:
                break

            if cell != self.DELETED and cell[0] == key:
                self.table[idx] = self.DELETED
                self.item_count -= 1
                steps.append(SimulationStep(
                    step_type="delete",
                    highlight_indices=[idx],
                    message=f"Deleted key {key} at index {idx}. Marked as DELETED tombstone."
                ))
                return SimulationResult(
                    algorithm_name="Linear Probing Delete",
                    success=True,
                    path=[idx],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Deleted key {key} at index {idx}."
                )

        return SimulationResult(
            algorithm_name="Linear Probing Delete",
            success=False,
            total_steps=len(steps),
            total_comparisons=probes,
            steps=steps,
            message=f"Key {key} not found for deletion."
        )

    def clear(self):
        self.table = [None] * self.size
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0


def preorder_traversal(root: Any) -> Tuple[List[int], List[SimulationStep]]:
    result: List[int] = []
    steps: List[SimulationStep] = []

    def _preorder(node: Any):
        if not node:
            return
        key = getattr(node, 'key', None)
        if key is not None:
            result.append(key)
            steps.append(SimulationStep(
                step_type="visit",
                current_element=key,
                visited_elements=list(result),
                message=f"Preorder visit: Node {key}."
            ))
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        if left:
            _preorder(left)
        if right:
            _preorder(right)

    _preorder(root)
    return result, steps


def inorder_traversal(root: Any) -> Tuple[List[int], List[SimulationStep]]:
    result: List[int] = []
    steps: List[SimulationStep] = []

    def _inorder(node: Any):
        if not node:
            return
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        key = getattr(node, 'key', None)

        if left:
            _inorder(left)
        if key is not None:
            result.append(key)
            steps.append(SimulationStep(
                step_type="visit",
                current_element=key,
                visited_elements=list(result),
                message=f"Inorder visit: Node {key}."
            ))
        if right:
            _inorder(right)

    _inorder(root)
    return result, steps


def postorder_traversal(root: Any) -> Tuple[List[int], List[SimulationStep]]:
    result: List[int] = []
    steps: List[SimulationStep] = []

    def _postorder(node: Any):
        if not node:
            return
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        key = getattr(node, 'key', None)

        if left:
            _postorder(left)
        if right:
            _postorder(right)
        if key is not None:
            result.append(key)
            steps.append(SimulationStep(
                step_type="visit",
                current_element=key,
                visited_elements=list(result),
                message=f"Postorder visit: Node {key}."
            ))

    _postorder(root)
    return result, steps


def levelorder_traversal(root: Any) -> Tuple[List[int], List[SimulationStep]]:
    result: List[int] = []
    steps: List[SimulationStep] = []

    if not root:
        return result, steps

    queue = deque([root])
    while queue:
        node = queue.popleft()
        key = getattr(node, 'key', None)
        if key is not None:
            result.append(key)
            steps.append(SimulationStep(
                step_type="visit",
                current_element=key,
                visited_elements=list(result),
                message=f"Level-order visit: Node {key}."
            ))
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        if left:
            queue.append(left)
        if right:
            queue.append(right)

    return result, steps


def get_tree_metrics(root: Any) -> Tuple[int, int, int]:
    if not root:
        return 0, 0, 0

    def _height(node: Any) -> int:
        if not node:
            return 0
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        return 1 + max(_height(left), _height(right))

    def _counts(node: Any) -> Tuple[int, int]:
        if not node:
            return 0, 0
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        if not left and not right:
            return 1, 1

        l_total, l_leaves = _counts(left)
        r_total, r_leaves = _counts(right)
        return 1 + l_total + r_total, l_leaves + r_leaves

    h = _height(root)
    tot, leaves = _counts(root)
    return h, tot, leaves


class BSTNode:
    def __init__(self, key: int):
        self.key = key
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None
        self.x: float = 0.0
        self.y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }


class BinarySearchTree:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []

        if self.root is None:
            self.root = BSTNode(key)
            steps.append(SimulationStep(
                step_type="insert_root",
                current_element=key,
                message=f"Inserted root node with key {key}."
            ))
            return SimulationResult(
                algorithm_name="BST Insert",
                success=True,
                total_steps=len(steps),
                steps=steps,
                message=f"Created BST root with key {key}."
            )

        curr = self.root
        while True:
            steps.append(SimulationStep(
                step_type="compare",
                current_element=curr.key,
                message=f"Comparing key {key} with current node {curr.key}."
            ))
            if key == curr.key:
                return SimulationResult(
                    algorithm_name="BST Insert",
                    success=False,
                    steps=steps,
                    message=f"Duplicate key {key} not inserted into BST."
                )
            elif key < curr.key:
                if curr.left is None:
                    curr.left = BSTNode(key)
                    steps.append(SimulationStep(
                        step_type="insert_left",
                        current_element=key,
                        message=f"Inserted key {key} as left child of {curr.key}."
                    ))
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = BSTNode(key)
                    steps.append(SimulationStep(
                        step_type="insert_right",
                        current_element=key,
                        message=f"Inserted key {key} as right child of {curr.key}."
                    ))
                    break
                curr = curr.right

        return SimulationResult(
            algorithm_name="BST Insert",
            success=True,
            total_steps=len(steps),
            steps=steps,
            message=f"Successfully inserted key {key} into BST."
        )

    def search(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        curr = self.root
        comparisons = 0

        while curr is not None:
            comparisons += 1
            steps.append(SimulationStep(
                step_type="probe",
                current_element=curr.key,
                message=f"Comparing key {key} with node {curr.key}."
            ))

            if key == curr.key:
                steps.append(SimulationStep(
                    step_type="found",
                    current_element=curr.key,
                    message=f"Key {key} found in BST after {comparisons} comparisons!"
                ))
                return SimulationResult(
                    algorithm_name="BST Search",
                    success=True,
                    path=[curr.key],
                    total_steps=len(steps),
                    total_comparisons=comparisons,
                    steps=steps,
                    message=f"Key {key} found in BST."
                )
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        steps.append(SimulationStep(
            step_type="not_found",
            message=f"Key {key} not found in BST."
        ))
        return SimulationResult(
            algorithm_name="BST Search",
            success=False,
            total_steps=len(steps),
            total_comparisons=comparisons,
            steps=steps,
            message=f"Key {key} not found."
        )

    def delete(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        deleted = [False]

        def _min_value_node(node: BSTNode) -> BSTNode:
            curr = node
            while curr.left is not None:
                curr = curr.left
            return curr

        def _delete_rec(root: Optional[BSTNode], k: int) -> Optional[BSTNode]:
            if root is None:
                return None

            if k < root.key:
                root.left = _delete_rec(root.left, k)
            elif k > root.key:
                root.right = _delete_rec(root.right, k)
            else:
                deleted[0] = True
                if root.left is None:
                    steps.append(SimulationStep(
                        step_type="delete_case1",
                        current_element=root.key,
                        message=f"Deleting node {root.key} (0 or 1 right child)."
                    ))
                    return root.right
                elif root.right is None:
                    steps.append(SimulationStep(
                        step_type="delete_case2",
                        current_element=root.key,
                        message=f"Deleting node {root.key} (1 left child)."
                    ))
                    return root.left

                succ = _min_value_node(root.right)
                steps.append(SimulationStep(
                    step_type="delete_case3",
                    current_element=root.key,
                    message=f"Node {root.key} has 2 children. Replacing with in-order successor {succ.key}."
                ))
                root.key = succ.key
                root.right = _delete_rec(root.right, succ.key)

            return root

        self.root = _delete_rec(self.root, key)

        if deleted[0]:
            return SimulationResult(
                algorithm_name="BST Delete",
                success=True,
                total_steps=len(steps),
                steps=steps,
                message=f"Successfully deleted key {key} from BST."
            )
        else:
            return SimulationResult(
                algorithm_name="BST Delete",
                success=False,
                message=f"Key {key} not present in BST."
            )

    def find_min(self) -> Optional[int]:
        if not self.root:
            return None
        curr = self.root
        while curr.left:
            curr = curr.left
        return curr.key

    def find_max(self) -> Optional[int]:
        if not self.root:
            return None
        curr = self.root
        while curr.right:
            curr = curr.right
        return curr.key

    def clear(self):
        self.root = None


class AVLNode:
    def __init__(self, key: int):
        self.key = key
        self.height: int = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None

    def get_balance_factor(self) -> int:
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        return left_h - right_h

    def update_height(self):
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        self.height = 1 + max(left_h, right_h)


class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance(self, node: Optional[AVLNode]) -> int:
        return node.get_balance_factor() if node else 0

    def _right_rotate(self, z: AVLNode, steps: List[SimulationStep]) -> AVLNode:
        y = z.left
        T3 = y.right if y else None

        steps.append(SimulationStep(
            step_type="rotation_LL",
            current_element=z.key,
            message=f"Executing Right Rotation (LL) on root node {z.key}."
        ))

        y.right = z
        z.left = T3

        z.update_height()
        y.update_height()
        return y

    def _left_rotate(self, z: AVLNode, steps: List[SimulationStep]) -> AVLNode:
        y = z.right
        T2 = y.left if y else None

        steps.append(SimulationStep(
            step_type="rotation_RR",
            current_element=z.key,
            message=f"Executing Left Rotation (RR) on root node {z.key}."
        ))

        y.left = z
        z.right = T2

        z.update_height()
        y.update_height()
        return y

    def insert(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []

        def _insert_rec(node: Optional[AVLNode], k: int) -> AVLNode:
            if not node:
                steps.append(SimulationStep(
                    step_type="insert",
                    current_element=k,
                    message=f"Inserted new AVL node {k}."
                ))
                return AVLNode(k)

            if k < node.key:
                node.left = _insert_rec(node.left, k)
            elif k > node.key:
                node.right = _insert_rec(node.right, k)
            else:
                return node

            node.update_height()
            balance = self._balance(node)

            steps.append(SimulationStep(
                step_type="check_balance",
                current_element=node.key,
                message=f"Node {node.key}: Height={node.height}, Balance Factor={balance}."
            ))

            if balance > 1 and k < node.left.key:
                return self._right_rotate(node, steps)

            if balance < -1 and k > node.right.key:
                return self._left_rotate(node, steps)

            if balance > 1 and k > node.left.key:
                steps.append(SimulationStep(
                    step_type="rotation_LR_step1",
                    current_element=node.left.key,
                    message=f"LR Rotation Step 1: Left rotate child {node.left.key}."
                ))
                node.left = self._left_rotate(node.left, steps)
                return self._right_rotate(node, steps)

            if balance < -1 and k < node.right.key:
                steps.append(SimulationStep(
                    step_type="rotation_RL_step1",
                    current_element=node.right.key,
                    message=f"RL Rotation Step 1: Right rotate child {node.right.key}."
                ))
                node.right = self._right_rotate(node.right, steps)
                return self._left_rotate(node, steps)

            return node

        self.root = _insert_rec(self.root, key)
        return SimulationResult(
            algorithm_name="AVL Insert",
            success=True,
            total_steps=len(steps),
            steps=steps,
            message=f"Inserted key {key} into AVL tree."
        )

    def search(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        curr = self.root
        probes = 0

        while curr:
            probes += 1
            steps.append(SimulationStep(
                step_type="probe",
                current_element=curr.key,
                message=f"Comparing key {key} with AVL node {curr.key} (BF: {curr.get_balance_factor()})."
            ))

            if key == curr.key:
                steps.append(SimulationStep(
                    step_type="found",
                    current_element=curr.key,
                    message=f"Key {key} found in AVL tree!"
                ))
                return SimulationResult(
                    algorithm_name="AVL Search",
                    success=True,
                    path=[curr.key],
                    total_steps=len(steps),
                    total_comparisons=probes,
                    steps=steps,
                    message=f"Key {key} found."
                )
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right

        return SimulationResult(
            algorithm_name="AVL Search",
            success=False,
            total_steps=len(steps),
            total_comparisons=probes,
            steps=steps,
            message=f"Key {key} not found in AVL tree."
        )

    def delete(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        deleted = [False]

        def _min_value_node(node: AVLNode) -> AVLNode:
            curr = node
            while curr.left:
                curr = curr.left
            return curr

        def _delete_rec(node: Optional[AVLNode], k: int) -> Optional[AVLNode]:
            if not node:
                return node

            if k < node.key:
                node.left = _delete_rec(node.left, k)
            elif k > node.key:
                node.right = _delete_rec(node.right, k)
            else:
                deleted[0] = True
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left

                temp = _min_value_node(node.right)
                node.key = temp.key
                node.right = _delete_rec(node.right, temp.key)

            if not node:
                return node

            node.update_height()
            balance = self._balance(node)

            if balance > 1 and self._balance(node.left) >= 0:
                return self._right_rotate(node, steps)

            if balance > 1 and self._balance(node.left) < 0:
                node.left = self._left_rotate(node.left, steps)
                return self._right_rotate(node, steps)

            if balance < -1 and self._balance(node.right) <= 0:
                return self._left_rotate(node, steps)

            if balance < -1 and self._balance(node.right) > 0:
                node.right = self._right_rotate(node.right, steps)
                return self._left_rotate(node, steps)

            return node

        self.root = _delete_rec(self.root, key)
        if deleted[0]:
            return SimulationResult(
                algorithm_name="AVL Delete",
                success=True,
                total_steps=len(steps),
                steps=steps,
                message=f"Deleted key {key} from AVL tree."
            )
        else:
            return SimulationResult(
                algorithm_name="AVL Delete",
                success=False,
                message=f"Key {key} not present in AVL tree."
            )

    def clear(self):
        self.root = None


class MinHeap:
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


class BTreeNode:
    def __init__(self, t: int, leaf: bool = True):
        self.t = t
        self.leaf = leaf
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keys": list(self.keys),
            "leaf": self.leaf,
            "children": [child.to_dict() for child in self.children]
        }


class BTree:
    def __init__(self, t: int = 3):
        self.t = t
        self.root: Optional[BTreeNode] = None

    def search(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []

        def _search_rec(node: Optional[BTreeNode], k: int) -> Tuple[Optional[BTreeNode], int]:
            if node is None:
                return None, -1

            i = 0
            while i < len(node.keys) and k > node.keys[i]:
                i += 1

            steps.append(SimulationStep(
                step_type="probe",
                current_element=k,
                message=f"Checking node with keys {node.keys}. Target {k} compared at slot {i}."
            ))

            if i < len(node.keys) and node.keys[i] == k:
                steps.append(SimulationStep(
                    step_type="found",
                    current_element=k,
                    message=f"Key {k} found in node keys {node.keys}!"
                ))
                return node, i

            if node.leaf:
                return None, -1

            return _search_rec(node.children[i], k)

        target_node, idx = _search_rec(self.root, key)
        if target_node:
            return SimulationResult(
                algorithm_name="B-Tree Search",
                success=True,
                steps=steps,
                message=f"Key {key} found in B-Tree."
            )
        else:
            return SimulationResult(
                algorithm_name="B-Tree Search",
                success=False,
                steps=steps,
                message=f"Key {key} not found in B-Tree."
            )

    def insert(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []

        if self.root is None:
            self.root = BTreeNode(self.t, leaf=True)
            self.root.keys.append(key)
            steps.append(SimulationStep(
                step_type="insert_root",
                current_element=key,
                message=f"Created B-Tree root with key {key}."
            ))
            return SimulationResult(algorithm_name="B-Tree Insert", success=True, steps=steps, message=f"Inserted {key}.")

        r = self.root
        if len(r.keys) == (2 * self.t - 1):
            s = BTreeNode(self.t, leaf=False)
            self.root = s
            s.children.append(r)
            self._split_child(s, 0, r, steps)
            self._insert_non_full(s, key, steps)
        else:
            self._insert_non_full(r, key, steps)

        return SimulationResult(
            algorithm_name="B-Tree Insert",
            success=True,
            total_steps=len(steps),
            steps=steps,
            message=f"Successfully inserted key {key} into B-Tree."
        )

    def _split_child(self, parent: BTreeNode, i: int, child: BTreeNode, steps: List[SimulationStep]):
        t = self.t
        z = BTreeNode(t, leaf=child.leaf)
        median_key = child.keys[t - 1]

        z.keys = child.keys[t:]
        child.keys = child.keys[:t - 1]

        if not child.leaf:
            z.children = child.children[t:]
            child.children = child.children[:t]

        parent.children.insert(i + 1, z)
        parent.keys.insert(i, median_key)

        steps.append(SimulationStep(
            step_type="split",
            current_element=median_key,
            message=f"Split full node. Promoted median key {median_key} into parent node."
        ))

    def _insert_non_full(self, node: BTreeNode, key: int, steps: List[SimulationStep]):
        i = len(node.keys) - 1

        if node.leaf:
            node.keys.append(0)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
            steps.append(SimulationStep(
                step_type="insert_leaf",
                current_element=key,
                message=f"Inserted key {key} into leaf node. Node keys now {node.keys}."
            ))
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == (2 * self.t - 1):
                self._split_child(node, i, node.children[i], steps)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, steps)

    def delete(self, key: int) -> SimulationResult:
        steps: List[SimulationStep] = []
        if not self.root:
            return SimulationResult(algorithm_name="B-Tree Delete", success=False, message="Tree empty.")

        deleted = [False]

        def _delete_node(node: BTreeNode, k: int):
            t = self.t
            idx = 0
            while idx < len(node.keys) and node.keys[idx] < k:
                idx += 1

            if idx < len(node.keys) and node.keys[idx] == k:
                deleted[0] = True
                if node.leaf:
                    node.keys.pop(idx)
                    steps.append(SimulationStep(
                        step_type="delete",
                        current_element=k,
                        message=f"Deleted key {k} from leaf node."
                    ))
                else:
                    if len(node.children[idx].keys) >= t:
                        pred = self._get_pred(node, idx)
                        node.keys[idx] = pred
                        _delete_node(node.children[idx], pred)
                    elif len(node.children[idx + 1].keys) >= t:
                        succ = self._get_succ(node, idx)
                        node.keys[idx] = succ
                        _delete_node(node.children[idx + 1], succ)
                    else:
                        self._merge(node, idx)
                        _delete_node(node.children[idx], k)
            else:
                if node.leaf:
                    return
                flag = (idx == len(node.keys))
                if idx < len(node.children) and len(node.children[idx].keys) < t:
                    self._fill(node, idx)
                if flag and idx > len(node.keys):
                    _delete_node(node.children[idx - 1], k)
                elif idx < len(node.children):
                    _delete_node(node.children[idx], k)

        _delete_node(self.root, key)
        if self.root and len(self.root.keys) == 0:
            self.root = self.root.children[0] if not self.root.leaf and self.root.children else None

        if deleted[0]:
            return SimulationResult(
                algorithm_name="B-Tree Delete",
                success=True,
                steps=steps,
                message=f"Successfully deleted key {key} from B-Tree."
            )
        else:
            return SimulationResult(
                algorithm_name="B-Tree Delete",
                success=False,
                message=f"Key {key} not found in B-Tree."
            )

    def _get_pred(self, node: BTreeNode, idx: int) -> int:
        curr = node.children[idx]
        while not curr.leaf:
            curr = curr.children[-1]
        return curr.keys[-1]

    def _get_succ(self, node: BTreeNode, idx: int) -> int:
        curr = node.children[idx + 1]
        while not curr.leaf:
            curr = curr.children[0]
        return curr.keys[0]

    def _fill(self, node: BTreeNode, idx: int):
        if idx != 0 and len(node.children[idx - 1].keys) >= self.t:
            self._borrow_from_prev(node, idx)
        elif idx != len(node.keys) and len(node.children[idx + 1].keys) >= self.t:
            self._borrow_from_next(node, idx)
        else:
            if idx != len(node.keys):
                self._merge(node, idx)
            else:
                self._merge(node, idx - 1)

    def _borrow_from_prev(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx - 1]

        child.keys.insert(0, node.keys[idx - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        node.keys[idx - 1] = sibling.keys.pop()

    def _borrow_from_next(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx + 1]

        child.keys.append(node.keys[idx])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        node.keys[idx] = sibling.keys.pop(0)

    def _merge(self, node: BTreeNode, idx: int):
        child = node.children[idx]
        sibling = node.children[idx + 1]

        child.keys.append(node.keys.pop(idx))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        node.children.pop(idx + 1)

    def clear(self):
        self.root = None


def parse_integer_list(input_str: str) -> Tuple[bool, List[int], str]:
    if not input_str.strip():
        return False, [], "Input text is empty."

    parts = input_str.replace(',', ' ').split()
    nums = []
    for p in parts:
        try:
            val = int(p.strip())
            nums.append(val)
        except ValueError:
            return False, [], f"Invalid integer token '{p}'."

    if not nums:
        return False, [], "No valid integers found in input."
    if len(nums) > 100:
        return False, [], "Maximum supported array size for visualization is 100."
    return True, nums, "Valid array."


def parse_integer(input_str: str) -> Tuple[bool, Optional[int], str]:
    try:
        val = int(input_str.strip())
        return True, val, "Valid integer."
    except ValueError:
        return False, None, "Please enter a valid integer."


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
    return COMPLEXITY_DATA.get(algorithm_name, {
        "time_best": "N/A",
        "time_avg": "N/A",
        "time_worst": "N/A",
        "space": "N/A",
        "description": "Algorithm complexity specification."
    })


class BenchmarkService:
    @staticmethod
    def benchmark_sorting(sizes: List[int] = [10, 50, 100, 200]) -> Dict[str, List[Dict[str, Any]]]:
        results = {
            "Bubble Sort": [],
            "Insertion Sort": [],
            "Selection Sort": [],
            "Merge Sort": []
        }

        random.seed(42)

        for size in sizes:
            arr = [random.randint(1, 1000) for _ in range(size)]

            res = bubble_sort(arr)
            results["Bubble Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            res = insertion_sort(arr)
            results["Insertion Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            res = selection_sort(arr)
            results["Selection Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

            res = merge_sort(arr)
            results["Merge Sort"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons,
                "swaps": res.total_swaps
            })

        return results

    @staticmethod
    def benchmark_searching(sizes: List[int] = [100, 500, 1000, 2000]) -> Dict[str, List[Dict[str, Any]]]:
        results = {
            "Linear Search": [],
            "Binary Search": [],
            "Interpolation Search": []
        }

        random.seed(42)

        for size in sizes:
            arr = sorted([random.randint(1, 10000) for _ in range(size)])
            target = arr[size // 2]

            res = linear_search(arr, target)
            results["Linear Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

            res = binary_search_iterative(arr, target)
            results["Binary Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

            res = interpolation_search(arr, target)
            results["Interpolation Search"].append({
                "size": size,
                "time_ms": res.execution_time_ms,
                "comparisons": res.total_comparisons
            })

        return results

    @staticmethod
    def benchmark_trees(num_ops: int = 500) -> Dict[str, Dict[str, Any]]:
        random.seed(42)
        keys = list(range(num_ops))

        bst = BinarySearchTree()
        t0 = time.perf_counter()
        for k in keys:
            bst.insert(k)
        bst_insert_time = (time.perf_counter() - t0) * 1000

        res_bst = bst.search(keys[-1])

        avl = AVLTree()
        t0 = time.perf_counter()
        for k in keys:
            avl.insert(k)
        avl_insert_time = (time.perf_counter() - t0) * 1000

        res_avl = avl.search(keys[-1])

        return {
            "BST": {
                "num_ops": num_ops,
                "insert_time_ms": bst_insert_time,
                "search_comparisons": res_bst.total_comparisons,
                "search_time_ms": res_bst.execution_time_ms
            },
            "AVL": {
                "num_ops": num_ops,
                "insert_time_ms": avl_insert_time,
                "search_comparisons": res_avl.total_comparisons,
                "search_time_ms": res_avl.execution_time_ms
            }
        }
