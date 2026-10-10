"""
Searching algorithms with step tracking and complex case handling (Linear, Binary, Interpolation).
"""
import time
from typing import List, Any
from models.simulation import SimulationStep, SimulationResult


def linear_search(arr: List[int], target: int) -> SimulationResult:
    """Linear Search algorithm."""
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

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
    """Binary Search algorithm (iterative). Requires sorted array."""
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

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
    """Binary Search algorithm (recursive wrapper)."""
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = [0]

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
    """
    Interpolation Search algorithm. Requires sorted array.
    Uses probe formula: pos = low + ((target - arr[low]) * (high - low)) // (arr[high] - arr[low])
    Handles duplicate endpoint values safely to prevent zero division.
    """
    start_time = time.perf_counter()
    steps: List[SimulationStep] = []
    comparisons = 0

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

        # Calculate probe position
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
