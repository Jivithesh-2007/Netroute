"""
Sorting algorithms (Bubble, Insertion, Selection, Merge) with step visualization tracking.
"""
import time
from typing import List
from models.simulation import SimulationStep, SimulationResult


def bubble_sort(arr_input: List[int]) -> SimulationResult:
    """Bubble Sort algorithm."""
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
    """Insertion Sort algorithm."""
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
    """Selection Sort algorithm."""
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
    """Merge Sort algorithm."""
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
