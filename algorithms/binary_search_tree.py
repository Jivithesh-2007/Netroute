"""
Binary Search Tree (BST) implementation with full node operations (Insert, Search, Delete).
Handles leaf deletion, single-child deletion, and two-children deletion via in-order successor.
"""
from typing import Optional, List, Dict, Any, Tuple
from models.simulation import SimulationStep, SimulationResult


class BSTNode:
    """Node in a Binary Search Tree."""

    def __init__(self, key: int):
        self.key = key
        self.left: Optional['BSTNode'] = None
        self.right: Optional['BSTNode'] = None
        self.x: float = 0.0
        self.y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert tree node structure to dictionary for Canvas rendering."""
        return {
            "key": self.key,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }


class BinarySearchTree:
    """Binary Search Tree supporting insert, search, and 3-case deletion."""

    def __init__(self):
        self.root: Optional[BSTNode] = None

    def insert(self, key: int) -> SimulationResult:
        """Insert a key into the BST."""
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
        """Search key in BST."""
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
        """Delete key from BST with leaf, 1-child, and 2-children cases."""
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
                # Case 1: Leaf node or single right child
                if root.left is None:
                    steps.append(SimulationStep(
                        step_type="delete_case1",
                        current_element=root.key,
                        message=f"Deleting node {root.key} (0 or 1 right child)."
                    ))
                    return root.right
                # Case 2: Single left child
                elif root.right is None:
                    steps.append(SimulationStep(
                        step_type="delete_case2",
                        current_element=root.key,
                        message=f"Deleting node {root.key} (1 left child)."
                    ))
                    return root.left

                # Case 3: Node with two children
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
        """Return minimum key in BST."""
        if not self.root:
            return None
        curr = self.root
        while curr.left:
            curr = curr.left
        return curr.key

    def find_max(self) -> Optional[int]:
        """Return maximum key in BST."""
        if not self.root:
            return None
        curr = self.root
        while curr.right:
            curr = curr.right
        return curr.key

    def clear(self):
        """Clear BST."""
        self.root = None
