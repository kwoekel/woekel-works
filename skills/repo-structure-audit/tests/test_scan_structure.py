#!/usr/bin/env python3
"""End-to-end regression tests for scan_structure.py."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCANNER = SKILL_DIR / "scripts" / "scan_structure.py"
SCHEMA = SKILL_DIR / "references" / "scan-schema.json"


class ScanStructureTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "repo"
        self.root.mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def write(self, relative_path, content="x\n"):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_scan(self, target=None, *extra, env=None):
        command = ["python3", str(SCANNER), str(target or self.root), *extra]
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})},
            check=False,
        )

    def scan_json(self, target=None, *extra, env=None):
        result = self.run_scan(target, *extra, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def init_git(self):
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "fixture@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Fixture"],
            check=True,
        )

    def commit_all(self, message):
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-q", "--allow-empty", "-m", message],
            check=True,
        )

    def test_refuses_output_inside_target_without_overwriting(self):
        readme = self.write("README.md", "original\n")

        result = self.run_scan(self.root, "--output", str(readme))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(readme.read_text(encoding="utf-8"), "original\n")
        self.assertIn("outside the target", result.stderr)

    def test_refuses_to_overwrite_existing_external_output(self):
        output = Path(self.tempdir.name) / "scan.json"
        output.write_text("keep me\n", encoding="utf-8")

        result = self.run_scan(self.root, "--output", str(output))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(encoding="utf-8"), "keep me\n")
        self.assertIn("already exists", result.stderr)

    def test_scoped_scan_detects_parent_git_repository(self):
        self.init_git()
        self.write("projects/app/README.md", "# App\n")
        self.commit_all("initial")

        report = self.scan_json(self.root / "projects" / "app")

        self.assertTrue(report["git"]["is_git_repo"])
        self.assertEqual(report["git"]["scope"], "subdirectory")

    def test_commit_count_is_exact_integer(self):
        self.init_git()
        self.write("README.md", "# Repo\n")
        for number in range(12):
            self.commit_all(f"commit {number}")

        report = self.scan_json()

        self.assertEqual(report["git"]["commit_count"], 12)
        self.assertIsInstance(report["git"]["commit_count"], int)

    def test_emits_bounded_directory_tree(self):
        self.write("README.md", "# Repo\n")
        self.write("projects/app/src/main.py", "print('ok')\n")

        report = self.scan_json()

        paths = {item["path"] for item in report["tree"]["directories"]}
        self.assertIn(".", paths)
        self.assertIn("projects/app/src", paths)
        self.assertFalse(report["tree"]["truncated"])

    def test_parses_nested_project_entry_points(self):
        self.write("README.md", "# Root\n")
        self.write("apps/api/package.json", "{}\n")
        self.write("apps/api/src/index.js", "export {};\n")
        self.write("apps/api/README.md", "# API\nSee [missing](docs/missing.md).\n")

        report = self.scan_json()

        nested = next(
            item for item in report["entry_points"] if item["path"] == "apps/api/README.md"
        )
        missing = nested["referenced_paths"]["missing"]
        self.assertEqual([item["path"] for item in missing], ["apps/api/docs/missing.md"])

    def test_generated_audit_reports_do_not_change_scan_facts(self):
        self.write("README.md", "# Repo\n")
        self.write(
            "audits/STRUCTURE-AUDIT-2026-08-15.md",
            "credential-secret duplicate duplicate obsolete\n",
        )

        report = self.scan_json()

        self.assertEqual(report["totals"]["files"], 1)
        self.assertNotIn("audits", report["lifecycle"]["empty_dirs"])
        self.assertEqual(report["coverage_gaps"]["generated_reports_excluded"], 1)

    def test_prohibited_paths_are_separate_from_missing_references(self):
        self.write("README.md", "Never create `tmp/` in this repository.\n")

        report = self.scan_json()

        refs = report["entry_points"][0]["referenced_paths"]
        self.assertEqual(refs["missing"], [])
        self.assertEqual([item["path"] for item in refs["prohibitions"]], ["tmp"])

    def test_zero_byte_sentinels_are_not_disposable_file_leads(self):
        self.write("inbox/.gitkeep", "")

        report = self.scan_json()

        self.assertNotIn("inbox/.gitkeep", report["lifecycle"]["zero_byte_files"])
        self.assertEqual(report["lifecycle"]["sentinel_files"], ["inbox/.gitkeep"])

    def test_gitignore_coverage_uses_git_pattern_semantics(self):
        self.init_git()
        self.write(".gitignore", "not-dist/\n")
        self.write("dist/app.js", "generated\n")
        self.commit_all("fixture")

        report = self.scan_json()

        self.assertIn("dist", report["git"]["artifact_dirs_not_in_gitignore"])

    def test_depth_limit_is_reported_only_when_a_directory_is_pruned(self):
        self.write("a/b/file.txt", "leaf\n")

        complete = self.scan_json(self.root, "--max-depth", "2")
        self.write("a/b/c/file.txt", "deeper\n")
        pruned = self.scan_json(self.root, "--max-depth", "2")

        self.assertFalse(complete["coverage_gaps"]["depth_limited"])
        self.assertTrue(pruned["coverage_gaps"]["depth_limited"])
        self.assertEqual(pruned["coverage_gaps"]["pruned_directories"], ["a/b/c"])

    def test_opaque_artifact_directories_are_named_as_coverage_gaps(self):
        self.write("vendor/library/source.py", "print('vendored')\n")

        report = self.scan_json()

        self.assertEqual(report["coverage_gaps"]["opaque_artifact_dirs"], ["vendor"])

    def test_root_layout_candidate_is_retained_when_top_cap_is_small(self):
        self.write("pyproject.toml", "[project]\nname='root'\n")
        self.write("src/main.py", "print('root')\n")
        for name in ("one", "two", "three"):
            self.write(f"packages/{name}/package.json", "{}\n")
            self.write(f"packages/{name}/src/index.js", "export {};\n")

        report = self.scan_json(self.root, "--top", "1")

        self.assertEqual(report["project_layout_candidates"][0]["path"], ".")

    def test_colocated_test_detection_ignores_artifact_trees(self):
        self.write("package.json", "{}\n")
        self.write("src/real.test.js", "test('real', () => {});\n")
        self.write("src/node_modules/pkg/generated.test.js", "test('generated', () => {});\n")

        report = self.scan_json()

        root_layout = next(
            item for item in report["project_layout_candidates"] if item["path"] == "."
        )
        self.assertFalse(root_layout["colocated_tests"])

    def test_out_of_root_references_are_classified_without_resolution(self):
        outside = Path(self.tempdir.name) / "private.txt"
        outside.write_text("private\n", encoding="utf-8")
        self.write("README.md", "See [private](../private.txt).\n")

        report = self.scan_json()

        refs = report["entry_points"][0]["referenced_paths"]
        self.assertEqual(refs["outside_target"], ["../private.txt"])
        self.assertEqual(refs["resolved"], 0)

    def test_output_matches_declared_top_level_schema(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        report = self.scan_json()

        self.assertEqual(report["scan"]["version"], schema["version"])
        for key in schema["required"]:
            self.assertIn(key, report)
        for key, definition in schema["properties"].items():
            expected = {"object": dict, "array": list, "string": str}[definition["type"]]
            self.assertIsInstance(report[key], expected)


if __name__ == "__main__":
    unittest.main()
