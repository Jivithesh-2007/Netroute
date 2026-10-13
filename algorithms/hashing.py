"""
Hash Table implementations for CO3: Separate Chaining and Open Addressing with Linear Probing.
Includes probe counting, collision tracking, deletion marker handling, and load factor calculation.
"""
from typing import List, Optional, Tuple, Any, Dict
from models.simulation import SimulationStep, SimulationResult


class HashTableChaining:
    """Hash Table using Separate Chaining (Linked List / Bucket Array)."""

    def __init__(self, size: int = 10):
        self.size = size
        self.buckets: List[List[Tuple[int, Any]]] = [[] for _ in range(size)]
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0

    def hash_function(self, key: int) -> int:
        """Division method hash function."""
        return abs(key) % self.size

    def get_load_factor(self) -> float:
        """Calculate load factor alpha = n / m."""
        return self.item_count / float(self.size)

    def insert(self, key: int, value: Any = None) -> SimulationResult:
        """Insert key into hash table using separate chaining."""
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

        # Check if key exists to update
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
        """Search key in separate chaining hash table."""
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
        """Delete key from separate chaining hash table."""
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
        """Reset hash table."""
        self.buckets = [[] for _ in range(self.size)]
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0


class HashTableLinearProbing:
    """
    Hash Table using Open Addressing with Linear Probing.
    Uses 'DELETED' tombstone markers to preserve search probes after deletion.
    """

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
        """Insert key using linear probing."""
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
        """Search key using linear probing."""
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
        """Delete key using linear probing (replaces cell with DELETED tombstone)."""
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
        """Clear linear probing table."""
        self.table = [None] * self.size
        self.item_count = 0
        self.collisions = 0
        self.total_probes = 0
