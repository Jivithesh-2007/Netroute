"""
Tree traversal algorithms (Preorder, Inorder, Postorder, Level-order)
with step tracking and tree metrics (height, node count, leaf count).
"""
from collections import deque
from typing import List, Tuple, Any, Optional
from models.simulation import SimulationStep, SimulationResult


def preorder_traversal(root: Any) -> Tuple[List[int], List[SimulationStep]]:
    """Preorder traversal (Root -> Left -> Right)."""
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
    """Inorder traversal (Left -> Root -> Right). Returns sorted sequence for BST."""
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
    """Postorder traversal (Left -> Right -> Root)."""
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
    """Level-order traversal (Breadth-First level-by-level)."""
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
    """
    Compute tree metrics:
    Returns (height, total_nodes, leaf_nodes).
    """
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
