#!/usr/bin/env python3
"""Behavior tests for the deterministic audit score calculator."""

import json
import os
import subprocess
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
CALCULATOR = SKILL_DIR / "scripts" / "calculate_score.py"


class CalculateScoreTests(unittest.TestCase):
    def run_score(self, *assignments):
        return subprocess.run(
            ["python3", str(CALCULATOR), "--json", *assignments],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )

    def test_pending_check_produces_assessed_denominator_and_range(self):
        result = self.run_score(
            "C1=100", "C2=100", "C3=100", "C4=100", "C5=100",
            "C6=100", "C7=100", "C8=pending", "C9=100", "C10=100",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        score = json.loads(result.stdout)
        self.assertEqual(score["assessed"], {"earned": 93, "available": 93, "percent": 100})
        self.assertEqual(score["full_score_range"], {"minimum": 93, "maximum": 100})
        self.assertEqual(score["groups"]["Lifecycle"]["available"], 18)
        self.assertEqual(score["groups"]["Lifecycle"]["pending"], 7)
        self.assertIsNone(score["final_score"])

    def test_resolved_score_returns_final_band(self):
        result = self.run_score(*(f"C{number}=100" for number in range(1, 11)))

        self.assertEqual(result.returncode, 0, result.stderr)
        score = json.loads(result.stdout)
        self.assertEqual(score["final_score"], 100)
        self.assertEqual(score["band"], "Maintained")

    def test_na_check_redistributes_points_within_group(self):
        assignments = [f"C{number}=100" for number in range(1, 9)]
        result = self.run_score(*assignments, "C9=80", "C10=na")

        self.assertEqual(result.returncode, 0, result.stderr)
        score = json.loads(result.stdout)
        self.assertEqual(score["groups"]["Hygiene"]["earned"], 20)
        self.assertEqual(score["groups"]["Hygiene"]["available"], 25)
        self.assertEqual(score["final_score"], 95)

    def test_rejects_non_rubric_percentage(self):
        assignments = [f"C{number}=100" for number in range(1, 11)]
        assignments[0] = "C1=70"

        result = self.run_score(*assignments)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allowed earned percentages", result.stderr)

    def test_text_output_labels_assessed_pending_and_group_total(self):
        assignments = [f"C{number}=100" for number in range(1, 11)]
        assignments[7] = "C8=pending"

        result = subprocess.run(
            ["python3", str(CALCULATOR), *assignments],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Lifecycle: 18/18 assessed; 7 pending (25 total)", result.stdout)


if __name__ == "__main__":
    unittest.main()
