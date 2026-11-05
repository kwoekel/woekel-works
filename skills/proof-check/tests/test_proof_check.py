#!/usr/bin/env python3
"""Behavior tests for the read-only court proof check."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "proof_check.py"

TIMELINE_HEAD = """> Organized draft for your attorney to review, not legal advice.

# Timeline

| # | Date | Precision | Event | Tag | Children involved | Sources |
|---|---|---|---|---|---|---|
"""
GOOD_ROWS = """| T-001 | 2024-03-02 | exact | Late exchange | 🔴 | yes | EVT-001, email 2024-03-02 "Pickup, late" |
| T-002 | 2024-04-10 | recollection | Phone call | 🟡 | no | [user provided] |
| T-003 | spring 2021 | approximate | School meeting | ⚪ | no | exports/notes.pdf |
"""


def entry(event_id="EVT-001", date="2024-03-02", precision="exact", reliability="primary",
          source_file="", body=""):
    return f"""---
date: {date}            # when it happened
date_precision: {precision}
type: incident
event_id: {event_id}
source_file: "{source_file}"
reliability: {reliability}
---

> Organized draft for your attorney to review, not legal advice.

# Short title
{body}
"""


class ProofCheckTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.court = self.root / "Case Files"
        (self.court / "incidents").mkdir(parents=True)
        (self.court / "communications").mkdir()
        (self.court / "exports").mkdir()
        (self.court / "exports" / "notes.pdf").write_text("x", encoding="utf-8")
        self.write_timeline(GOOD_ROWS)
        self.write_entry("a.md", entry())

    def write_timeline(self, rows):
        (self.court / "timeline.md").write_text(TIMELINE_HEAD + rows, encoding="utf-8")

    def write_entry(self, name, text, folder="incidents"):
        (self.court / folder / name).write_text(text, encoding="utf-8")

    def check(self, draft):
        path = self.root / "draft.md"
        path.write_text(draft, encoding="utf-8")
        return self.run_script(str(path), str(self.court))

    def run_script(self, *args):
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )

    def events(self, *paragraphs):
        return "## Events\n\n" + "\n\n".join(paragraphs) + "\n"

    def assert_clean(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no problems found", result.stdout)

    def assert_problem(self, result, *phrases):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        for phrase in phrases:
            self.assertIn(phrase, result.stdout)

    def test_clean_draft_passes_and_keeps_disclaimer(self):
        result = self.check(self.events("On March 2, 2024 the exchange ran late. [T-001; EVT-001]"))

        self.assert_clean(result)
        self.assertIn("Organized draft for your attorney to review, not legal advice.", result.stdout)

    def test_never_changes_the_folder(self):
        def snapshot():
            return {
                path: (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()
            }

        draft = self.root / "draft.md"
        draft.write_text(self.events("Uncited paragraph.", "Bad [T-999]"), encoding="utf-8")
        before = snapshot()

        self.run_script(str(draft), str(self.court))

        self.assertEqual(snapshot(), before)

    def test_reports_unknown_cited_ids(self):
        result = self.check(self.events("Something happened. [T-999; EVT-404, COM-777]"))

        self.assert_problem(result, "T-999 isn't in", "EVT-404 isn't in", "COM-777 isn't in")

    def test_accepts_slash_separated_and_linked_ids(self):
        result = self.check(
            "## Key incidents\n\n- Late exchange [T-001 / EVT-001]\n- Linked [T-001](timeline.md)\n"
        )

        self.assert_clean(result)

    def test_reports_timeline_source_id_that_does_not_exist(self):
        self.write_timeline('| T-001 | 2024-03-02 | exact | Event | 🔴 | yes | EVT-050 |\n')

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "T-001", "lists EVT-050")

    def test_reports_timeline_source_file_that_does_not_exist(self):
        self.write_timeline('| T-001 | 2024-03-02 | exact | Event | 🔴 | yes | exports/gone.pdf |\n')

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "points to exports/gone.pdf")

    def test_reports_timeline_row_with_no_sources(self):
        self.write_timeline('| T-001 | 2024-03-02 | exact | Event | 🔴 | yes |  |\n')

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "lists no source at all")

    def test_source_paths_resolve_whatever_the_folder_is_called(self):
        self.write_timeline('| T-001 | 2024-03-02 | exact | Event | 🔴 | yes | court/exports/notes.pdf |\n')

        self.assert_clean(self.check(self.events("Event. [T-001]")))

    def test_reports_entry_source_file_that_does_not_exist(self):
        self.write_entry("b.md", entry("EVT-002", source_file="exports/missing.png"))

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "EVT-002", "points to exports/missing.png")

    def test_reports_entry_evidence_table_file_but_not_plain_words(self):
        body = """
## Evidence
| Evidence | Where it lives | Strength |
|---|---|---|
| Photo | exports/photo.jpg | ★★★ |
| Texts | User's phone | ★★☆ |
| Note | EVT-090 | ★☆☆ |
"""
        self.write_entry("b.md", entry("EVT-002", body=body))

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "points to exports/photo.jpg", "lists EVT-090")
        self.assertNotIn("points to User's phone", result.stdout)
        self.assertIn("User's phone", result.stdout)

    def test_flags_uncited_paragraph_only_under_events(self):
        result = self.check(
            "## Background\n\nNo citation needed here.\n\n"
            "## Events\n\nThis one has none.\n\nThis one does. [T-001]\n\n"
            "## Patterns\n\nNone here either.\n"
        )

        self.assert_problem(result, "Line 7", "This one has none")
        self.assertNotIn("No citation needed", result.stdout)
        self.assertNotIn("None here either", result.stdout)

    def test_placeholder_brackets_are_not_citations(self):
        result = self.check(self.events("Details pending. [to fill in later]"))

        self.assert_problem(result, "Details pending")

    def test_words_source_counts_as_citation_but_is_listed_for_reading(self):
        result = self.check(self.events('A message came in. [text 2023-05-04]'))

        self.assert_clean(result)
        self.assertIn("described in words", result.stdout)
        self.assertIn("text 2023-05-04", result.stdout)

    def test_bare_date_bracket_is_not_a_citation(self):
        result = self.check("## Key incidents\n\n- [2024-03-02] Late exchange\n")

        self.assert_problem(result, "Late exchange")

    def test_statement_of_facts_counts_as_events(self):
        result = self.check("## Statement of facts\n\nUncited fact.\n")

        self.assert_problem(result, "Uncited fact")

    def test_reports_missing_events_section(self):
        result = self.check("## Summary\n\nJust a summary.\n")

        self.assert_problem(result, "No Events section found")

    def test_quote_block_belongs_to_the_paragraph_above(self):
        result = self.check(self.events('The message said: [T-001]\n\n> "See you at noon."'))

        self.assert_clean(result)

    def test_table_and_code_block_are_not_paragraphs(self):
        result = self.check(self.events(
            "| A | B |\n|---|---|\n| 1 | 2 |",
            "```\nExample without citation T-999\n```",
            "Real paragraph. [T-001]",
        ))

        self.assert_clean(result)

    def test_reports_date_mismatch_in_each_format(self):
        for wording in ("2024-03-05", "March 5, 2024", "3/5/2024", "Mar. 5th, 2024", "5 March 2024"):
            with self.subTest(wording=wording):
                result = self.check(self.events(f"On {wording} it ran late. [T-001]"))

                self.assert_problem(result, f'says "{wording}"', "T-001 is dated 2024-03-02")

    def test_accepts_matching_dates_at_coarser_precision(self):
        for wording in ("March 2024", "March 2", "3/2/24", "March 2nd, 2024"):
            with self.subTest(wording=wording):
                self.assert_clean(self.check(self.events(f"In {wording} it ran late. [T-001]")))

    def test_reports_wrong_month(self):
        result = self.check(self.events("In April 2024 it ran late. [T-001]"))

        self.assert_problem(result, 'says "April 2024"')

    def test_date_may_match_any_cited_row_or_cited_source(self):
        draft = self.events(
            "On 2024-03-02 and 2024-04-10, to the best of my recollection, two things. [T-001, T-002]",
            "The reply came 2024-03-03. [T-001; text 2024-03-03]",
        )

        self.assert_clean(self.check(draft))

    def test_date_inside_a_citation_is_not_compared_to_the_row(self):
        self.assert_clean(self.check(self.events("It ran late. [T-001; email 2020-01-01]")))

    def test_compares_entry_dates_ignoring_frontmatter_comment(self):
        result = self.check(self.events("On 2024-03-09 it ran late. [EVT-001]"))

        self.assert_problem(result, 'says "2024-03-09"', "EVT-001 is dated 2024-03-02")

    def test_unreadable_row_date_is_a_note_not_a_problem(self):
        result = self.check(self.events("On 2021-04-01 we met. [T-003]"))

        self.assert_clean(result)
        self.assertIn("couldn't compare dates", result.stdout)

    def test_reports_recollection_row_without_the_phrase(self):
        result = self.check(self.events("We spoke by phone. [T-002]"))

        self.assert_problem(result, "cites T-002", "to the best of my recollection")

    def test_accepts_recollection_phrase_in_any_case_across_lines(self):
        draft = self.events("To the best\nof my Recollection, we spoke by phone. [T-002]")

        self.assert_clean(self.check(draft))

    def test_reports_recollection_entry_without_the_phrase(self):
        self.write_entry("b.md", entry("EVT-002", reliability="recollection"))
        self.write_entry("c.md", entry("COM-001", precision="recollection"), folder="communications")

        result = self.check(self.events("Told from memory. [EVT-002]", "Also memory. [COM-001]"))

        self.assert_problem(result, "cites EVT-002", "cites COM-001")

    def test_unfilled_template_precision_is_not_recollection(self):
        self.write_entry("b.md", entry("EVT-002", precision="exact | approximate | recollection"))

        self.assert_clean(self.check(self.events("It happened. [EVT-002]")))

    def test_reports_duplicate_ids(self):
        self.write_entry("b.md", entry("EVT-001"))

        result = self.check(self.events("Event. [T-001]"))

        self.assert_problem(result, "EVT-001 is used twice")

    def test_entry_without_event_id_is_noted(self):
        self.write_entry("b.md", "# Hand-written note\n")

        result = self.check(self.events("Event. [T-001]"))

        self.assert_clean(result)
        self.assertIn("no usable event_id", result.stdout)

    def test_missing_timeline_fails_plainly(self):
        (self.court / "timeline.md").unlink()

        result = self.check(self.events("Event. [EVT-001]"))

        self.assert_problem(result, "No timeline.md")

    def test_bad_arguments_exit_one_in_plain_words(self):
        missing_file = self.run_script(str(self.root / "nope.md"), str(self.court))
        missing_folder = self.run_script(str(SCRIPT), str(self.root / "nope"))
        no_arguments = self.run_script()

        self.assertEqual(missing_file.returncode, 1)
        self.assertIn("can't find the file", missing_file.stderr)
        self.assertEqual(missing_folder.returncode, 1)
        self.assertIn("can't find the folder", missing_folder.stderr)
        self.assertEqual(no_arguments.returncode, 1)
        self.assertNotIn("Traceback", no_arguments.stderr)


if __name__ == "__main__":
    unittest.main()
