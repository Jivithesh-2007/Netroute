"""
Unit tests for input validation utilities, simulation service, benchmark service, and complexity helpers.
"""
import unittest
from utils.validation import validate_router_id, parse_integer_list, parse_integer
from utils.complexity import get_complexity_info
from services.simulation_service import SimulationService
from services.benchmark_service import BenchmarkService
from models.simulation import SimulationStep, SimulationResult


class TestValidationAndServices(unittest.TestCase):

    def test_validate_router_id(self):
        valid, msg = validate_router_id("R1")
        self.assertTrue(valid)
        self.assertEqual(msg, "R1")

        valid, _ = validate_router_id("")
        self.assertFalse(valid)

        valid, _ = validate_router_id("R@#$")
        self.assertFalse(valid)

        valid, _ = validate_router_id("VERYLONGRID12345")
        self.assertFalse(valid)

    def test_parse_integer_list(self):
        valid, nums, _ = parse_integer_list("10, 20 30, 40")
        self.assertTrue(valid)
        self.assertEqual(nums, [10, 20, 30, 40])

        valid, _, _ = parse_integer_list("10, abc, 30")
        self.assertFalse(valid)

        valid, _, _ = parse_integer_list("   ")
        self.assertFalse(valid)

    def test_parse_integer(self):
        valid, val, _ = parse_integer("42")
        self.assertTrue(valid)
        self.assertEqual(val, 42)

        valid, val, _ = parse_integer("abc")
        self.assertFalse(valid)

    def test_simulation_service_controls(self):
        service = SimulationService()
        steps = [
            SimulationStep(step_type="init", message="Step 1"),
            SimulationStep(step_type="compare", message="Step 2")
        ]
        res = SimulationResult(algorithm_name="TestAlg", success=True, steps=steps)

        callback_data = []

        def _on_step(step, current, total):
            callback_data.append((step.message, current, total))

        service.load_simulation(res, on_step=_on_step)
        self.assertEqual(len(service.steps), 2)

        # Step forward
        service.step_forward()
        self.assertEqual(len(callback_data), 1)
        self.assertEqual(callback_data[0][0], "Step 1")

        service.step_forward()
        self.assertEqual(len(callback_data), 2)
        self.assertEqual(callback_data[1][0], "Step 2")

        # Speed setting
        service.set_speed(300)
        self.assertEqual(service.speed_ms, 300)

        service.stop()
        self.assertEqual(service.current_step_index, -1)

    def test_benchmark_service(self):
        sort_res = BenchmarkService.benchmark_sorting([10])
        self.assertIn("Bubble Sort", sort_res)
        self.assertEqual(len(sort_res["Bubble Sort"]), 1)

        search_res = BenchmarkService.benchmark_searching([50])
        self.assertIn("Binary Search", search_res)

        tree_res = BenchmarkService.benchmark_trees(50)
        self.assertIn("BST", tree_res)
        self.assertIn("AVL", tree_res)

    def test_complexity_info(self):
        info = get_complexity_info("BFS Routing")
        self.assertEqual(info["time_worst"], "O(V + E)")

        fallback = get_complexity_info("Unknown Alg")
        self.assertEqual(fallback["time_best"], "N/A")


if __name__ == "__main__":
    unittest.main()
