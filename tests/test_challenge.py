"""
test_challenge.py — Automated Tests for DSA Challenge Mode.
Verifies challenge question definitions, evaluation against genuine algorithm results,
and feedback explanations.
"""

import unittest
from network import Graph
from algorithms import bfs, dijkstra
from simulation import CHALLENGES, evaluate_challenge_answer


class TestChallengeMode(unittest.TestCase):
    def test_challenges_defined_and_structured(self):
        """Verifies that all challenges contain necessary educational and validation fields."""
        self.assertGreaterEqual(len(CHALLENGES), 4)
        for ch in CHALLENGES:
            self.assertIn("id", ch)
            self.assertIn("title", ch)
            self.assertIn("question", ch)
            self.assertIn("options", ch)
            self.assertIn("correct_option", ch)
            self.assertIn("explanation", ch)
            self.assertIn(ch["correct_option"], ch["options"])

    def test_challenge_evaluations_accuracy(self):
        """Verifies evaluate_challenge_answer returns True for correct and False for wrong answers."""
        for ch in CHALLENGES:
            cid = ch["id"]
            correct = ch["correct_option"]
            is_ok, expl = evaluate_challenge_answer(cid, correct)
            self.assertTrue(is_ok)
            self.assertEqual(expl, ch["explanation"])

            # Test wrong answer
            is_wrong, _ = evaluate_challenge_answer(cid, "Completely Random Wrong Answer")
            self.assertFalse(is_wrong)

    def test_challenge_answers_match_genuine_algorithm_results(self):
        """Verifies challenge answers are mathematically consistent with real graph execution."""
        # Challenge 1: BFS on reference network
        g_ref = Graph()
        g_ref.load_preset("reference")
        b_res = bfs(g_ref, "N1", "N7")
        self.assertEqual(" -> ".join(b_res["path"]), "N1 -> N2 -> N4 -> N6 -> N7")

        # Challenge 2: BFS vs Dijkstra on weighted comparison network
        g_diff = Graph()
        g_diff.load_preset("weighted_diff")
        b_diff = bfs(g_diff, "S", "D")
        d_diff = dijkstra(g_diff, "S", "D")
        self.assertEqual(" -> ".join(b_diff["path"]), "S -> A -> D")
        self.assertEqual(b_diff["hops"], 2)
        self.assertEqual(b_diff["path_cost"], 13.0)
        self.assertEqual(" -> ".join(d_diff["path"]), "S -> A -> B -> D")
        self.assertEqual(d_diff["hops"], 3)
        self.assertEqual(d_diff["path_cost"], 4.0)

        # Challenge 3: Articulation failure of N6 isolates N7
        g_ref.toggle_router_status("N6")
        self.assertFalse(g_ref.is_reachable("N1", "N7"))


if __name__ == "__main__":
    unittest.main()
