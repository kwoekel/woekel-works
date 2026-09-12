#!/usr/bin/env python3
"""Contract tests for the reader-facing HTML audit template."""

import unittest
from html.parser import HTMLParser
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_DIR / "assets" / "structure-audit.template.html"


class TemplateParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section_ids = []
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section":
            self.section_ids.append(attributes.get("id"))
        if tag == "script":
            self.scripts += 1


class ReportTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TEMPLATE.read_text(encoding="utf-8")
        cls.parser = TemplateParser()
        cls.parser.feed(cls.source)

    def test_template_is_standalone_html(self):
        self.assertTrue(self.source.startswith("<!doctype html>"))
        self.assertIn("<meta name=\"viewport\"", self.source)
        self.assertIn("<style>", self.source)
        self.assertEqual(self.parser.scripts, 0)
        self.assertNotIn("http://", self.source)
        self.assertNotIn("https://", self.source)

    def test_report_keeps_exact_reading_path(self):
        self.assertEqual(
            self.parser.section_ids,
            ["what-current-state", "so-what", "now-what"],
        )
        for heading in (
            "What: Current State",
            "So What: What This Affects",
            "Now What: Proposed Changes",
        ):
            self.assertIn(heading, self.source)

    def test_report_keeps_review_and_coverage_boundaries_visible(self):
        self.assertIn("Read-only review — nothing changed", self.source)
        self.assertIn("Proposed — not reviewed", self.source)
        self.assertIn("Coverage and security limits", self.source)
        self.assertIn("Never quote secret values", self.source)

    def test_template_supports_narrow_and_print_layouts(self):
        self.assertIn("min-width: 0", self.source)
        self.assertIn("@media (max-width: 760px)", self.source)
        self.assertIn("@media print", self.source)


if __name__ == "__main__":
    unittest.main()
