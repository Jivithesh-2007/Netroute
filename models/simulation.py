"""
Simulation models for execution tracking and step-by-step state representations.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SimulationStep:
    """Represents a single step in an algorithm simulation."""
    step_type: str  # e.g., 'visit', 'enqueue', 'pop', 'compare', 'swap', 'probe', 'found', 'backtrack'
    current_element: Optional[Any] = None
    data_structure_state: Optional[List[Any]] = None  # Queue/Stack/Array state
    visited_elements: List[Any] = field(default_factory=list)
    active_path: List[Any] = field(default_factory=list)
    message: str = ""
    highlight_indices: List[int] = field(default_factory=list)
    secondary_indices: List[int] = field(default_factory=list)
    extra_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Summary of an algorithm simulation run."""
    algorithm_name: str
    success: bool
    path: List[Any] = field(default_factory=list)
    visited_order: List[Any] = field(default_factory=list)
    total_steps: int = 0
    total_comparisons: int = 0
    total_swaps: int = 0
    execution_time_ms: float = 0.0
    steps: List[SimulationStep] = field(default_factory=list)
    message: str = ""
