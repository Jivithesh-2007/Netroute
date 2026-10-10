"""
Simulation execution service managing step-by-step non-blocking animation playback.
"""
from typing import Callable, Optional, List, Any
from models.simulation import SimulationStep, SimulationResult


class SimulationService:
    """Manages playback controls (Play, Pause, Step, Speed, Reset) for canvas simulations."""

    def __init__(self, root_widget: Optional[Any] = None):
        self.root = root_widget
        self.steps: List[SimulationStep] = []
        self.current_step_index: int = -1
        self.is_running: bool = False
        self.is_paused: bool = False
        self.speed_ms: int = 500  # Default delay in ms
        self._timer_id: Optional[str] = None
        self.on_step_callback: Optional[Callable[[SimulationStep, int, int], None]] = None
        self.on_complete_callback: Optional[Callable[[], None]] = None

    def load_simulation(
        self,
        result: SimulationResult,
        on_step: Callable[[SimulationStep, int, int], None],
        on_complete: Optional[Callable[[], None]] = None
    ):
        """Load steps from a simulation result."""
        self.stop()
        self.steps = result.steps
        self.current_step_index = -1
        self.on_step_callback = on_step
        self.on_complete_callback = on_complete

    def play(self):
        """Start or resume playback."""
        if not self.steps:
            return
        self.is_running = True
        self.is_paused = False
        self._schedule_next_step()

    def pause(self):
        """Pause playback."""
        self.is_paused = True
        self.is_running = False
        self._cancel_timer()

    def stop(self):
        """Stop and reset playback state."""
        self.is_running = False
        self.is_paused = False
        self._cancel_timer()
        self.current_step_index = -1

    def step_forward(self):
        """Advance one step manually."""
        if not self.steps:
            return
        if self.current_step_index + 1 < len(self.steps):
            self.current_step_index += 1
            step = self.steps[self.current_step_index]
            if self.on_step_callback:
                self.on_step_callback(step, self.current_step_index + 1, len(self.steps))

    def set_speed(self, delay_ms: int):
        """Set animation delay in milliseconds."""
        self.speed_ms = max(50, min(2000, delay_ms))

    def _schedule_next_step(self):
        self._cancel_timer()
        if not self.is_running or self.is_paused:
            return

        if self.current_step_index + 1 < len(self.steps):
            self.current_step_index += 1
            step = self.steps[self.current_step_index]
            if self.on_step_callback:
                self.on_step_callback(step, self.current_step_index + 1, len(self.steps))

            if self.root:
                self._timer_id = self.root.after(self.speed_ms, self._schedule_next_step)
        else:
            self.is_running = False
            if self.on_complete_callback:
                self.on_complete_callback()

    def _cancel_timer(self):
        if self._timer_id and self.root:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
