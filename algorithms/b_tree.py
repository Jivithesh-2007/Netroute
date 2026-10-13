"""
B-Tree data structure with configurable minimum degree 't',
multi-key node splitting, search, insert, and deletion handling.
"""
from typing import List, Optional, Tuple, Dict, Any
from models.simulation import SimulationStep, SimulationResult


class BTreeNode:
    """Node in a B-Tree holding up to (2*t - 1) keys."""

    def __init__(self, t: int, leaf: bool = True):
        self.t = t
        self.leaf = leaf
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert B-Tree node to dictionary for Canvas rendering."""
        return {
            "keys": list(self.keys),
            "leaf": self.leaf,
            "children": [child.to_dict() for child in self.children]
        }


class BTree:
    """B-Tree implementation with minimum degree t."""

    def __init__(self, t: int = 3):
        self.t = t
        self.root: Optional[BTreeNode] = None

    def search(self, key: int) -> SimulationResult:
        """Search key in B-Tree."""
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
        """Insert key into B-Tree with node splitting when full."""
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
        """Split a full child node."""
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
        """Insert key into a non-full B-Tree node."""
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
        """Delete key from B-Tree."""
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
                    # Replace with predecessor if available
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
