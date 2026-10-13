"""
Self-balancing AVL Tree with LL, RR, LR, and RL rotations, balance factor calculations,
and node insert/delete operations.
"""
from typing import Optional, List, Dict, Any
from models.simulation import SimulationStep, SimulationResult


class AVLNode:
    """Node in an AVL Tree."""

    def __init__(self, key: int):
        self.key = key
        self.height: int = 1
        self.left: Optional['AVLNode'] = None
        self.right: Optional['AVLNode'] = None

    def get_balance_factor(self) -> int:
        """Balance Factor = height(left) - height(right)."""
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        return left_h - right_h

    def update_height(self):
        """Update node height based on children."""
        left_h = self.left.height if self.left else 0
        right_h = self.right.height if self.right else 0
        self.height = 1 + max(left_h, right_h)


class AVLTree:
    """Self-balancing AVL Tree."""

    def __init__(self):
        self.root: Optional[AVLNode] = None

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _balance(self, node: Optional[AVLNode]) -> int:
        return node.get_balance_factor() if node else 0

    def _right_rotate(self, z: AVLNode, steps: List[SimulationStep]) -> AVLNode:
        """Right rotation (LL Rotation)."""
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
        """Left rotation (RR Rotation)."""
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
        """Insert key into AVL Tree and rebalance as necessary."""
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

            # Left Left Case
            if balance > 1 and k < node.left.key:
                return self._right_rotate(node, steps)

            # Right Right Case
            if balance < -1 and k > node.right.key:
                return self._left_rotate(node, steps)

            # Left Right Case
            if balance > 1 and k > node.left.key:
                steps.append(SimulationStep(
                    step_type="rotation_LR_step1",
                    current_element=node.left.key,
                    message=f"LR Rotation Step 1: Left rotate child {node.left.key}."
                ))
                node.left = self._left_rotate(node.left, steps)
                return self._right_rotate(node, steps)

            # Right Left Case
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
        """Search key in AVL Tree."""
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
        """Delete key from AVL tree and rebalance."""
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
