import time
import random
from typing import List, Dict, Tuple, Optional, Any
from network import SimulationStep, SimulationResult

def parse_integer(txt: str) -> Tuple[bool, Optional[int], str]:
    cleaned = txt.strip()
    if not cleaned:
        return False, None, "Input cannot be empty."
    try:
        val = int(cleaned)
        return True, val, ""
    except ValueError:
        return False, None, f"'{cleaned}' is not a valid integer."

def parse_integer_list(txt: str) -> Tuple[bool, List[int], str]:
    cleaned = txt.strip()
    if not cleaned:
        return False, [], "Input array cannot be empty."
    tokens = [t.strip() for t in cleaned.replace(",", " ").split() if t.strip()]
    res = []
    for t in tokens:
        try:
            res.append(int(t))
        except ValueError:
            return False, [], f"'{t}' is not a valid integer."
    if not res:
        return False, [], "Array must contain at least one integer."
    return True, res, ""

def linear_search(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    found_idx = -1

    for i in range(len(arr)):
        comparisons += 1
        steps.append(SimulationStep(
            step_type="compare",
            current_element=arr[i],
            data_structure_state=list(arr),
            highlight_indices=[i],
            message=f"Comparing index [{i}]: {arr[i]} == {target}?"
        ))
        if arr[i] == target:
            found_idx = i
            steps.append(SimulationStep(
                step_type="found",
                current_element=arr[i],
                data_structure_state=list(arr),
                highlight_indices=[i],
                message=f"Target {target} discovered at index [{i}] after {comparisons} comparisons."
            ))
            break

    if found_idx == -1:
        steps.append(SimulationStep(
            step_type="not_found",
            data_structure_state=list(arr),
            message=f"Target {target} not present in array after {comparisons} comparisons."
        ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Linear Search",
        success=(found_idx != -1),
        path=[found_idx] if found_idx != -1 else [],
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Found at [{found_idx}]" if found_idx != -1 else "Not found"
    )

def binary_search_iterative(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    found_idx = -1
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        steps.append(SimulationStep(
            step_type="compare",
            current_element=arr[mid],
            data_structure_state=list(arr),
            highlight_indices=[mid],
            secondary_indices=[low, high],
            message=f"Subarray [{low}..{high}]: mid=[{mid}] val={arr[mid]}, target={target}"
        ))

        if arr[mid] == target:
            found_idx = mid
            steps.append(SimulationStep(
                step_type="found",
                current_element=arr[mid],
                data_structure_state=list(arr),
                highlight_indices=[mid],
                message=f"Target {target} discovered at index [{mid}]."
            ))
            break
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    if found_idx == -1:
        steps.append(SimulationStep(
            step_type="not_found",
            data_structure_state=list(arr),
            message=f"Target {target} not found in sorted array."
        ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Binary Search (Iterative)",
        success=(found_idx != -1),
        path=[found_idx] if found_idx != -1 else [],
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Found at [{found_idx}]" if found_idx != -1 else "Not found"
    )

def binary_search_recursive(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = [0]

    def _rec(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = (low + high) // 2
        comparisons[0] += 1
        steps.append(SimulationStep(
            step_type="compare",
            current_element=arr[mid],
            data_structure_state=list(arr),
            highlight_indices=[mid],
            secondary_indices=[low, high],
            message=f"Recursive call [{low}..{high}]: mid=[{mid}] val={arr[mid]}"
        ))
        if arr[mid] == target:
            steps.append(SimulationStep(
                step_type="found",
                current_element=arr[mid],
                data_structure_state=list(arr),
                highlight_indices=[mid],
                message=f"Target {target} discovered at index [{mid}]."
            ))
            return mid
        elif arr[mid] < target:
            return _rec(mid + 1, high)
        else:
            return _rec(low, mid - 1)

    found_idx = _rec(0, len(arr) - 1)
    if found_idx == -1:
        steps.append(SimulationStep(
            step_type="not_found",
            data_structure_state=list(arr),
            message=f"Target {target} not found in sorted array."
        ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Binary Search (Recursive)",
        success=(found_idx != -1),
        path=[found_idx] if found_idx != -1 else [],
        total_steps=len(steps),
        total_comparisons=comparisons[0],
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Found at [{found_idx}]" if found_idx != -1 else "Not found"
    )

def interpolation_search(arr: List[int], target: int) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0
    found_idx = -1
    low = 0
    high = len(arr) - 1

    while low <= high and target >= arr[low] and target <= arr[high]:
        if low == high:
            comparisons += 1
            if arr[low] == target:
                found_idx = low
            break

        if arr[high] == arr[low]:
            if arr[low] == target:
                found_idx = low
            break

        pos = low + int(((float(high - low) / (arr[high] - arr[low])) * (target - arr[low])))
        pos = max(low, min(high, pos))

        comparisons += 1
        steps.append(SimulationStep(
            step_type="probe",
            current_element=arr[pos],
            data_structure_state=list(arr),
            highlight_indices=[pos],
            secondary_indices=[low, high],
            message=f"Interpolated probe at pos=[{pos}] val={arr[pos]} for target={target}"
        ))

        if arr[pos] == target:
            found_idx = pos
            steps.append(SimulationStep(
                step_type="found",
                current_element=arr[pos],
                data_structure_state=list(arr),
                highlight_indices=[pos],
                message=f"Target {target} found at probe pos [{pos}]."
            ))
            break
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1

    if found_idx == -1:
        steps.append(SimulationStep(
            step_type="not_found",
            data_structure_state=list(arr),
            message=f"Target {target} not found via interpolation search."
        ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Interpolation Search",
        success=(found_idx != -1),
        path=[found_idx] if found_idx != -1 else [],
        total_steps=len(steps),
        total_comparisons=comparisons,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Found at [{found_idx}]" if found_idx != -1 else "Not found"
    )

def bubble_sort(arr: List[int]) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    a = list(arr)
    n = len(a)
    comparisons = 0
    swaps = 0

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(a),
        message="Initialized array for Bubble Sort."
    ))

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(a),
                highlight_indices=[j, j + 1],
                message=f"Comparing a[{j}]={a[j]} and a[{j+1}]={a[j+1]}"
            ))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
                steps.append(SimulationStep(
                    step_type="swap",
                    data_structure_state=list(a),
                    highlight_indices=[j, j + 1],
                    message=f"Swapped: a[{j}]={a[j]}, a[{j+1}]={a[j+1]}"
                ))
        if not swapped:
            break

    steps.append(SimulationStep(
        step_type="complete",
        data_structure_state=list(a),
        message=f"Bubble Sort completed. Comparisons: {comparisons}, Swaps: {swaps}"
    ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Bubble Sort",
        success=True,
        path=a,
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=swaps,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Sorted {n} elements in {elapsed:.2f} ms"
    )

def insertion_sort(arr: List[int]) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    a = list(arr)
    n = len(a)
    comparisons = 0
    writes = 0

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(a),
        message="Initialized array for Insertion Sort."
    ))

    for i in range(1, n):
        key = a[i]
        j = i - 1
        steps.append(SimulationStep(
            step_type="select",
            data_structure_state=list(a),
            highlight_indices=[i],
            message=f"Selected key a[{i}] = {key} to insert into sorted prefix [0..{i-1}]."
        ))
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                writes += 1
                steps.append(SimulationStep(
                    step_type="shift",
                    data_structure_state=list(a),
                    highlight_indices=[j + 1],
                    message=f"Shifted {a[j]} right to index [{j+1}]."
                ))
                j -= 1
            else:
                break
        a[j + 1] = key
        writes += 1
        steps.append(SimulationStep(
            step_type="insert",
            data_structure_state=list(a),
            highlight_indices=[j + 1],
            message=f"Placed key {key} at index [{j+1}]."
        ))

    steps.append(SimulationStep(
        step_type="complete",
        data_structure_state=list(a),
        message=f"Insertion Sort complete. Comparisons: {comparisons}, Writes: {writes}."
    ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Insertion Sort",
        success=True,
        path=a,
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=writes,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Sorted {n} elements in {elapsed:.2f} ms"
    )

def selection_sort(arr: List[int]) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    a = list(arr)
    n = len(a)
    comparisons = 0
    swaps = 0

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(a),
        message="Initialized array for Selection Sort."
    ))

    for i in range(n):
        min_idx = i
        steps.append(SimulationStep(
            step_type="select",
            data_structure_state=list(a),
            highlight_indices=[i],
            message=f"Pass {i+1}: Assuming minimum is at index [{i}] ({a[i]})."
        ))
        for j in range(i + 1, n):
            comparisons += 1
            steps.append(SimulationStep(
                step_type="compare",
                data_structure_state=list(a),
                highlight_indices=[j],
                secondary_indices=[min_idx],
                message=f"Comparing a[{j}]={a[j]} with current min a[{min_idx}]={a[min_idx]}."
            ))
            if a[j] < a[min_idx]:
                min_idx = j
                steps.append(SimulationStep(
                    step_type="update_min",
                    data_structure_state=list(a),
                    highlight_indices=[min_idx],
                    message=f"New minimum found: a[{min_idx}]={a[min_idx]}."
                ))
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
            steps.append(SimulationStep(
                step_type="swap",
                data_structure_state=list(a),
                highlight_indices=[i, min_idx],
                message=f"Swapped minimum {a[i]} into position [{i}]."
            ))

    steps.append(SimulationStep(
        step_type="complete",
        data_structure_state=list(a),
        message=f"Selection Sort complete. Comparisons: {comparisons}, Swaps: {swaps}."
    ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Selection Sort",
        success=True,
        path=a,
        total_steps=len(steps),
        total_comparisons=comparisons,
        total_swaps=swaps,
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Sorted {n} elements in {elapsed:.2f} ms"
    )

def merge_sort(arr: List[int]) -> SimulationResult:
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    a = list(arr)
    comparisons = [0]
    writes = [0]

    def _merge(left: int, mid: int, right: int):
        L = a[left:mid + 1]
        R = a[mid + 1:right + 1]
        i = j = 0
        k = left
        while i < len(L) and j < len(R):
            comparisons[0] += 1
            if L[i] <= R[j]:
                a[k] = L[i]
                i += 1
            else:
                a[k] = R[j]
                j += 1
            writes[0] += 1
            steps.append(SimulationStep(
                step_type="merge_write",
                data_structure_state=list(a),
                highlight_indices=[k],
                message=f"Merged element {a[k]} into position [{k}]."
            ))
            k += 1
        while i < len(L):
            a[k] = L[i]
            writes[0] += 1
            i += 1
            k += 1
        while j < len(R):
            a[k] = R[j]
            writes[0] += 1
            j += 1
            k += 1

    def _sort(left: int, right: int):
        if left < right:
            mid = (left + right) // 2
            _sort(left, mid)
            _sort(mid + 1, right)
            _merge(left, mid, right)

    steps.append(SimulationStep(
        step_type="init",
        data_structure_state=list(a),
        message="Initialized array for Merge Sort."
    ))

    if a:
        _sort(0, len(a) - 1)

    steps.append(SimulationStep(
        step_type="complete",
        data_structure_state=list(a),
        message=f"Merge Sort complete. Comparisons: {comparisons[0]}, Writes: {writes[0]}."
    ))

    elapsed = (time.perf_counter() - start_time) * 1000.0
    return SimulationResult(
        algorithm_name="Merge Sort",
        success=True,
        path=a,
        total_steps=len(steps),
        total_comparisons=comparisons[0],
        total_swaps=writes[0],
        execution_time_ms=elapsed,
        steps=steps,
        message=f"Sorted {len(a)} elements in {elapsed:.2f} ms"
    )

def schedule_tasks(tasks: List[Dict[str, Any]], sort_by: str = "priority") -> Tuple[List[Dict[str, Any]], str]:
    t = [dict(item) for item in tasks]
    if sort_by == "priority":
        t.sort(key=lambda x: (x.get("priority", 99), x.get("deadline", 99)))
        rationale = "Ordered by Priority (Highest/Lowest rank first) to ensure critical system packets and routing syncs execute first."
    elif sort_by == "deadline":
        t.sort(key=lambda x: (x.get("deadline", 99), x.get("priority", 99)))
        rationale = "Ordered by Earliest Deadline First (EDF) to minimize total packet delay and SLA violations."
    else:
        t.sort(key=lambda x: x.get("duration", 99))
        rationale = "Ordered by Shortest Job First (SJF) to minimize average queuing wait time."

    cum_time = 0
    for task in t:
        cum_time += task.get("duration", 1)
        task["completion_time"] = cum_time
        task["slack"] = task.get("deadline", 99) - cum_time

    return t, rationale

class HashTableChaining:
    def __init__(self, size: int = 7):
        self.size = size
        self.buckets: List[List[Tuple[int, Any]]] = [[] for _ in range(size)]
        self.total_elements = 0

    def hash_fn(self, key: int) -> int:
        return abs(key) % self.size

    def insert(self, key: int, val: Any = None) -> Tuple[bool, str, int]:
        idx = self.hash_fn(key)
        for i, (k, _) in enumerate(self.buckets[idx]):
            if k == key:
                self.buckets[idx][i] = (key, val)
                return True, f"Key {key} updated in bucket [{idx}].", idx
        self.buckets[idx].append((key, val))
        self.total_elements += 1
        coll = len(self.buckets[idx]) - 1
        msg = f"Key {key} inserted in bucket [{idx}]" + (f" (Collision resolved via chain length {coll+1})" if coll > 0 else "")
        return True, msg, idx

    def search(self, key: int) -> Tuple[bool, Optional[Any], int, int]:
        idx = self.hash_fn(key)
        probes = 0
        for k, v in self.buckets[idx]:
            probes += 1
            if k == key:
                return True, v, idx, probes
        return False, None, idx, probes

    def delete(self, key: int) -> Tuple[bool, str, int]:
        idx = self.hash_fn(key)
        for i, (k, _) in enumerate(self.buckets[idx]):
            if k == key:
                del self.buckets[idx][i]
                self.total_elements -= 1
                return True, f"Key {key} deleted from bucket [{idx}].", idx
        return False, f"Key {key} not found.", idx

    def load_factor(self) -> float:
        return self.total_elements / self.size if self.size > 0 else 0.0

    def get_state(self) -> List[Tuple[int, List[int]]]:
        return [(i, [k for k, _ in self.buckets[i]]) for i in range(self.size)]

class HashTableLinearProbing:
    def __init__(self, size: int = 7):
        self.size = size
        self.keys: List[Optional[int]] = [None] * size
        self.values: List[Optional[Any]] = [None] * size
        self.is_deleted: List[bool] = [False] * size
        self.total_elements = 0

    def hash_fn(self, key: int) -> int:
        return abs(key) % self.size

    def insert(self, key: int, val: Any = None) -> Tuple[bool, str, List[int]]:
        if self.total_elements >= self.size:
            return False, "Hash table is full (load factor 1.0). Cannot insert.", []

        idx = self.hash_fn(key)
        probe_path = []
        first_tombstone = None

        for step in range(self.size):
            curr = (idx + step) % self.size
            probe_path.append(curr)

            if self.keys[curr] == key and not self.is_deleted[curr]:
                self.values[curr] = val
                return True, f"Key {key} updated at index [{curr}].", probe_path

            if self.is_deleted[curr] and first_tombstone is None:
                first_tombstone = curr

            if self.keys[curr] is None:
                target = first_tombstone if first_tombstone is not None else curr
                self.keys[target] = key
                self.values[target] = val
                self.is_deleted[target] = False
                self.total_elements += 1
                return True, f"Key {key} placed at index [{target}] after {len(probe_path)} probes.", probe_path

        if first_tombstone is not None:
            self.keys[first_tombstone] = key
            self.values[first_tombstone] = val
            self.is_deleted[first_tombstone] = False
            self.total_elements += 1
            return True, f"Key {key} reused tombstone slot [{first_tombstone}].", probe_path

        return False, "Hash table full.", probe_path

    def search(self, key: int) -> Tuple[bool, Optional[Any], List[int]]:
        idx = self.hash_fn(key)
        probe_path = []
        for step in range(self.size):
            curr = (idx + step) % self.size
            probe_path.append(curr)
            if self.keys[curr] == key and not self.is_deleted[curr]:
                return True, self.values[curr], probe_path
            if self.keys[curr] is None and not self.is_deleted[curr]:
                break
        return False, None, probe_path

    def delete(self, key: int) -> Tuple[bool, str, List[int]]:
        idx = self.hash_fn(key)
        probe_path = []
        for step in range(self.size):
            curr = (idx + step) % self.size
            probe_path.append(curr)
            if self.keys[curr] == key and not self.is_deleted[curr]:
                self.is_deleted[curr] = True
                self.total_elements -= 1
                return True, f"Key {key} deleted (marked tombstone at [{curr}]).", probe_path
            if self.keys[curr] is None and not self.is_deleted[curr]:
                break
        return False, f"Key {key} not found.", probe_path

    def load_factor(self) -> float:
        return self.total_elements / self.size if self.size > 0 else 0.0

    def get_state(self) -> List[Tuple[int, Optional[int], str]]:
        res = []
        for i in range(self.size):
            if self.is_deleted[i]:
                status = "Tombstone"
                k = self.keys[i]
            elif self.keys[i] is not None:
                status = "Occupied"
                k = self.keys[i]
            else:
                status = "Empty"
                k = None
            res.append((i, k, status))
        return res

class BSTNode:
    def __init__(self, val: int):
        self.val = val
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None

class BinarySearchTree:
    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, val: int) -> bool:
        if not self.root:
            self.root = BSTNode(val)
            return True
        curr = self.root
        while True:
            if val == curr.val:
                return False
            elif val < curr.val:
                if not curr.left:
                    curr.left = BSTNode(val)
                    return True
                curr = curr.left
            else:
                if not curr.right:
                    curr.right = BSTNode(val)
                    return True
                curr = curr.right

    def search(self, val: int) -> Tuple[bool, List[int]]:
        path = []
        curr = self.root
        while curr:
            path.append(curr.val)
            if val == curr.val:
                return True, path
            curr = curr.left if val < curr.val else curr.right
        return False, path

    def delete(self, val: int) -> bool:
        def _del(node: Optional[BSTNode], key: int) -> Tuple[Optional[BSTNode], bool]:
            if not node:
                return None, False
            if key < node.val:
                node.left, res = _del(node.left, key)
                return node, res
            elif key > node.val:
                node.right, res = _del(node.right, key)
                return node, res
            else:
                if not node.left and not node.right:
                    return None, True
                if not node.left:
                    return node.right, True
                if not node.right:
                    return node.left, True
                succ = node.right
                while succ.left:
                    succ = succ.left
                node.val = succ.val
                node.right, _ = _del(node.right, succ.val)
                return node, True

        self.root, success = _del(self.root, val)
        return success

    def traversals(self) -> Dict[str, List[int]]:
        in_order, pre_order, post_order, level_order = [], [], [], []
        def _in(n):
            if n:
                _in(n.left)
                in_order.append(n.val)
                _in(n.right)
        def _pre(n):
            if n:
                pre_order.append(n.val)
                _pre(n.left)
                _pre(n.right)
        def _post(n):
            if n:
                _post(n.left)
                _post(n.right)
                post_order.append(n.val)

        _in(self.root)
        _pre(self.root)
        _post(self.root)

        if self.root:
            q = [self.root]
            while q:
                c = q.pop(0)
                level_order.append(c.val)
                if c.left:
                    q.append(c.left)
                if c.right:
                    q.append(c.right)

        return {
            "inorder": in_order,
            "preorder": pre_order,
            "postorder": post_order,
            "levelorder": level_order
        }

    def get_metrics(self) -> Dict[str, Any]:
        def _h(n):
            return 0 if not n else 1 + max(_h(n.left), _h(n.right))
        def _leaves(n):
            if not n:
                return 0
            if not n.left and not n.right:
                return 1
            return _leaves(n.left) + _leaves(n.right)

        in_ord = self.traversals()["inorder"]
        return {
            "height": _h(self.root),
            "leaf_count": _leaves(self.root),
            "min_val": in_ord[0] if in_ord else None,
            "max_val": in_ord[-1] if in_ord else None,
            "total_nodes": len(in_ord)
        }

class AVLNode:
    def __init__(self, val: int):
        self.val = val
        self.height = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None

class AVLTree:
    def __init__(self):
        self.root: Optional[AVLNode] = None

    def height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def balance_factor(self, node: Optional[AVLNode]) -> int:
        return self.height(node.left) - self.height(node.right) if node else 0

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        x.height = 1 + max(self.height(x.left), self.height(x.right))
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        x.height = 1 + max(self.height(x.left), self.height(x.right))
        y.height = 1 + max(self.height(y.left), self.height(y.right))
        return y

    def insert(self, val: int) -> Tuple[bool, str]:
        rotation_log = []

        def _ins(node: Optional[AVLNode], key: int) -> Tuple[AVLNode, bool]:
            if not node:
                return AVLNode(key), True
            if key == node.val:
                return node, False
            if key < node.val:
                node.left, res = _ins(node.left, key)
            else:
                node.right, res = _ins(node.right, key)
            if not res:
                return node, False

            node.height = 1 + max(self.height(node.left), self.height(node.right))
            bf = self.balance_factor(node)

            if bf > 1 and key < node.left.val:
                rotation_log.append(f"LL Rotation on node {node.val}")
                return self._rotate_right(node), True
            if bf < -1 and key > node.right.val:
                rotation_log.append(f"RR Rotation on node {node.val}")
                return self._rotate_left(node), True
            if bf > 1 and key > node.left.val:
                rotation_log.append(f"LR Rotation on node {node.val}")
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node), True
            if bf < -1 and key < node.right.val:
                rotation_log.append(f"RL Rotation on node {node.val}")
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node), True

            return node, True

        self.root, success = _ins(self.root, val)
        msg = f"Inserted {val}" + (f" with {', '.join(rotation_log)}" if rotation_log else " (Balanced)")
        return success, msg

    def delete(self, val: int) -> Tuple[bool, str]:
        rotation_log = []

        def _del(node: Optional[AVLNode], key: int) -> Tuple[Optional[AVLNode], bool]:
            if not node:
                return None, False
            if key < node.val:
                node.left, res = _del(node.left, key)
            elif key > node.val:
                node.right, res = _del(node.right, key)
            else:
                if not node.left or not node.right:
                    temp = node.left if node.left else node.right
                    return temp, True
                else:
                    succ = node.right
                    while succ.left:
                        succ = succ.left
                    node.val = succ.val
                    node.right, _ = _del(node.right, succ.val)
                    res = True

            if not node:
                return None, res

            node.height = 1 + max(self.height(node.left), self.height(node.right))
            bf = self.balance_factor(node)

            if bf > 1 and self.balance_factor(node.left) >= 0:
                rotation_log.append(f"LL Rotation on node {node.val}")
                return self._rotate_right(node), True
            if bf > 1 and self.balance_factor(node.left) < 0:
                rotation_log.append(f"LR Rotation on node {node.val}")
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node), True
            if bf < -1 and self.balance_factor(node.right) <= 0:
                rotation_log.append(f"RR Rotation on node {node.val}")
                return self._rotate_left(node), True
            if bf < -1 and self.balance_factor(node.right) > 0:
                rotation_log.append(f"RL Rotation on node {node.val}")
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node), True

            return node, True

        self.root, success = _del(self.root, val)
        msg = f"Deleted {val}" + (f" with {', '.join(rotation_log)}" if rotation_log else "")
        return success, msg

    def search(self, val: int) -> Tuple[bool, List[int]]:
        path = []
        c = self.root
        while c:
            path.append(c.val)
            if val == c.val:
                return True, path
            c = c.left if val < c.val else c.right
        return False, path

    def get_balance_factors(self) -> Dict[int, int]:
        bfs = {}
        def _walk(n):
            if n:
                bfs[n.val] = self.balance_factor(n)
                _walk(n.left)
                _walk(n.right)
        _walk(self.root)
        return bfs

class MinHeap:
    def __init__(self):
        self.heap: List[int] = []

    def insert(self, val: int):
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def extract(self) -> Optional[int]:
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def peek(self) -> Optional[int]:
        return self.heap[0] if self.heap else None

    def build_heap(self, arr: List[int]):
        self.heap = list(arr)
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, idx: int):
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx] < self.heap[parent]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int):
        smallest = idx
        n = len(self.heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < n and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break

    def get_array(self) -> List[int]:
        return list(self.heap)

class MaxHeap:
    def __init__(self):
        self.heap: List[int] = []

    def insert(self, val: int):
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def extract(self) -> Optional[int]:
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def peek(self) -> Optional[int]:
        return self.heap[0] if self.heap else None

    def build_heap(self, arr: List[int]):
        self.heap = list(arr)
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, idx: int):
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx] > self.heap[parent]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int):
        largest = idx
        n = len(self.heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < n and self.heap[left] > self.heap[largest]:
                largest = left
            if right < n and self.heap[right] > self.heap[largest]:
                largest = right
            if largest != idx:
                self.heap[idx], self.heap[largest] = self.heap[largest], self.heap[idx]
                idx = largest
            else:
                break

    def get_array(self) -> List[int]:
        return list(self.heap)

class BTreeNode:
    def __init__(self, leaf: bool = False):
        self.leaf = leaf
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []

class BTree:
    def __init__(self, t: int = 2):
        self.root = BTreeNode(leaf=True)
        self.t = t

    def insert(self, key: int) -> bool:
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            s = BTreeNode(leaf=False)
            self.root = s
            s.children.append(root)
            self._split_child(s, 0)
            return self._insert_non_full(s, key)
        else:
            return self._insert_non_full(root, key)

    def _split_child(self, x: BTreeNode, i: int):
        t = self.t
        y = x.children[i]
        z = BTreeNode(leaf=y.leaf)
        z.keys = y.keys[t:]
        mid_key = y.keys[t - 1]
        y.keys = y.keys[:t - 1]
        if not y.leaf:
            z.children = y.children[t:]
            y.children = y.children[:t]
        x.children.insert(i + 1, z)
        x.keys.insert(i, mid_key)

    def _insert_non_full(self, x: BTreeNode, key: int) -> bool:
        if key in x.keys:
            return False
        i = len(x.keys) - 1
        if x.leaf:
            while i >= 0 and key < x.keys[i]:
                i -= 1
            x.keys.insert(i + 1, key)
            return True
        else:
            while i >= 0 and key < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                if key > x.keys[i]:
                    i += 1
                elif key == x.keys[i]:
                    return False
            return self._insert_non_full(x.children[i], key)

    def search(self, key: int, node: Optional[BTreeNode] = None) -> bool:
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == key:
            return True
        if node.leaf:
            return False
        return self.search(key, node.children[i])

    def delete(self, key: int) -> bool:
        all_keys = self.traverse()
        if key not in all_keys:
            return False
        all_keys.remove(key)
        self.root = BTreeNode(leaf=True)
        for k in all_keys:
            self.insert(k)
        return True

    def traverse(self, node: Optional[BTreeNode] = None) -> List[int]:
        if node is None:
            node = self.root
        res = []
        if node.leaf:
            res.extend(node.keys)
        else:
            for i in range(len(node.keys)):
                res.extend(self.traverse(node.children[i]))
                res.append(node.keys[i])
            if node.children:
                res.extend(self.traverse(node.children[-1]))
        return res

COMPLEXITY_DATA = {
    "Linear Search": {"time_best": "O(1)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"},
    "Binary Search": {"time_best": "O(1)", "time_avg": "O(log N)", "time_worst": "O(log N)", "space": "O(1)"},
    "Interpolation Search": {"time_best": "O(1)", "time_avg": "O(log log N)", "time_worst": "O(N)", "space": "O(1)"},
    "Bubble Sort": {"time_best": "O(N)", "time_avg": "O(N^2)", "time_worst": "O(N^2)", "space": "O(1)"},
    "Insertion Sort": {"time_best": "O(N)", "time_avg": "O(N^2)", "time_worst": "O(N^2)", "space": "O(1)"},
    "Selection Sort": {"time_best": "O(N^2)", "time_avg": "O(N^2)", "time_worst": "O(N^2)", "space": "O(1)"},
    "Merge Sort": {"time_best": "O(N log N)", "time_avg": "O(N log N)", "time_worst": "O(N log N)", "space": "O(N)"},
    "Hash Chaining": {"time_best": "O(1)", "time_avg": "O(1)", "time_worst": "O(N)", "space": "O(N)"},
    "Hash Linear Probing": {"time_best": "O(1)", "time_avg": "O(1)", "time_worst": "O(N)", "space": "O(N)"},
    "BST Search": {"time_best": "O(1)", "time_avg": "O(log N)", "time_worst": "O(N)", "space": "O(N)"},
    "AVL Search": {"time_best": "O(1)", "time_avg": "O(log N)", "time_worst": "O(log N)", "space": "O(N)"},
    "Heap Extract": {"time_best": "O(1)", "time_avg": "O(log N)", "time_worst": "O(log N)", "space": "O(N)"},
    "B-Tree Search": {"time_best": "O(1)", "time_avg": "O(log N)", "time_worst": "O(log N)", "space": "O(N)"},
    "BFS Routing": {"time_best": "O(1)", "time_avg": "O(V + E)", "time_worst": "O(V + E)", "space": "O(V)"},
    "DFS Routing": {"time_best": "O(1)", "time_avg": "O(V + E)", "time_worst": "O(V + E)", "space": "O(V)"}
}

def get_complexity_info(name: str) -> Dict[str, str]:
    return COMPLEXITY_DATA.get(name, {"time_best": "O(1)", "time_avg": "O(N)", "time_worst": "O(N)", "space": "O(1)"})

class BenchmarkService:
    @staticmethod
    def benchmark_sorting(sizes: List[int] = [50, 100, 200]) -> Dict[str, List[Tuple[int, float, int]]]:
        res = {
            "Bubble Sort": [],
            "Insertion Sort": [],
            "Selection Sort": [],
            "Merge Sort": []
        }
        for s in sizes:
            arr = [random.randint(1, 1000) for _ in range(s)]
            r_bubble = bubble_sort(arr)
            res["Bubble Sort"].append((s, r_bubble.execution_time_ms, r_bubble.total_comparisons))
            r_ins = insertion_sort(arr)
            res["Insertion Sort"].append((s, r_ins.execution_time_ms, r_ins.total_comparisons))
            r_sel = selection_sort(arr)
            res["Selection Sort"].append((s, r_sel.execution_time_ms, r_sel.total_comparisons))
            r_mrg = merge_sort(arr)
            res["Merge Sort"].append((s, r_mrg.execution_time_ms, r_mrg.total_comparisons))
        return res

    @staticmethod
    def benchmark_searching(sizes: List[int] = [100, 500, 1000]) -> Dict[str, List[Tuple[int, float, int]]]:
        res = {
            "Linear Search": [],
            "Binary Search": []
        }
        for s in sizes:
            arr = sorted([random.randint(1, 5000) for _ in range(s)])
            target = arr[s // 2]
            r_lin = linear_search(arr, target)
            res["Linear Search"].append((s, r_lin.execution_time_ms, r_lin.total_comparisons))
            r_bin = binary_search_iterative(arr, target)
            res["Binary Search"].append((s, r_bin.execution_time_ms, r_bin.total_comparisons))
        return res

    @staticmethod
    def benchmark_trees(num_items: int = 100) -> Dict[str, float]:
        arr = list(range(1, num_items + 1))
        t0 = time.perf_counter()
        bst = BinarySearchTree()
        for x in arr:
            bst.insert(x)
        bst_time = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        avl = AVLTree()
        for x in arr:
            avl.insert(x)
        avl_time = (time.perf_counter() - t0) * 1000.0

        return {
            "BST": bst_time,
            "AVL": avl_time
        }
