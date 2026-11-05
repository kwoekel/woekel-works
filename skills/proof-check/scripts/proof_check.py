#!/usr/bin/env python3
"""Check a court narrative or packet against the court folder. Read-only.

Usage: proof_check.py DRAFT.md COURT_FOLDER
Exit 0: no problems found. Exit 1: problems found, or the check could not run.
"""

import argparse
import calendar
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote


DISCLAIMER = "Organized draft for your attorney to review, not legal advice."
RECOLLECTION_PHRASE = "to the best of my recollection"
ENTRY_FOLDERS = ("incidents", "communications")
MAX_TO_READ_SHOWN = 10

ID_RE = re.compile(r"\b(?:T|EVT|COM)-\d+\b")
LINK_RE = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^)\s]*)\)")
BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
QUOTED_RE = re.compile(r'"[^"]*"|“[^”]*”')
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
RULE_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
FILE_EXT_RE = re.compile(r"\.[A-Za-z][A-Za-z0-9]{0,4}$")
WEB_RE = re.compile(r"^(?:[a-z]+://|www\.)|\.(?:com|org|net|gov|edu)$", re.IGNORECASE)
USER_PROVIDED_RE = re.compile(r"^user provided$", re.IGNORECASE)
FACT_SECTION_RE = re.compile(
    r"^(?:events|statement of facts|since our last contact|key incidents)\b",
    re.IGNORECASE,
)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
MONTH = (
    "January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|"
    "September|Sept|Sep|October|Oct|November|Nov|December|Dec"
)


def month_number(name):
    return MONTHS[name[:3].lower()]


def full_year(text):
    year = int(text)
    return year + 2000 if year < 100 else year


# Most specific first; each match is blanked so a shorter pattern can't reuse it.
DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b"),
     lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b"),
     lambda m: (full_year(m[3]), int(m[1]), int(m[2]))),
    (re.compile(rf"\b({MONTH})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b"),
     lambda m: (int(m[3]), month_number(m[1]), int(m[2]))),
    (re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH})\.?,?\s+(\d{{4}})\b"),
     lambda m: (int(m[3]), month_number(m[2]), int(m[1]))),
    (re.compile(rf"\b({MONTH})\.?,?\s+(?:of\s+)?(\d{{4}})\b"),
     lambda m: (int(m[2]), month_number(m[1]), None)),
    (re.compile(r"\b(\d{4})-(\d{2})\b"),
     lambda m: (int(m[1]), int(m[2]), None)),
    (re.compile(rf"\b({MONTH})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?\b"),
     lambda m: (None, month_number(m[1]), int(m[2]))),
]


def valid_date(value):
    year, month, day = value
    if not 1 <= month <= 12:
        return False
    if day is None:
        return True
    return 1 <= day <= calendar.monthrange(year or 2000, month)[1]


def find_dates(text):
    """Return (original wording, (year, month, day)) pairs; year or day may be None."""
    found = []
    for pattern, build in DATE_PATTERNS:
        def take(match):
            value = build(match)
            if valid_date(value):
                found.append((match.start(), match.group(0), value))
            return " " * len(match.group(0))

        text = pattern.sub(take, text)
    return [(wording, value) for _, wording, value in sorted(found, key=lambda item: item[0])]


def dates_match(first, second):
    return all(a is None or b is None or a == b for a, b in zip(first, second))


@dataclass
class Citation:
    ids: list = field(default_factory=list)
    files: list = field(default_factory=list)
    words: list = field(default_factory=list)
    user_provided: bool = False


@dataclass
class Record:
    record_id: str
    date_text: str
    recollection: bool
    location: str


@dataclass
class Unit:
    line: int
    text: str
    in_fact_section: bool


@dataclass
class Report:
    problems: dict = field(default_factory=dict)
    to_read: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def add(self, category, message):
        self.problems.setdefault(category, []).append(message)


NOWHERE_CITATIONS = "Citations that lead nowhere"
NOWHERE_SOURCES = "Timeline rows and entries whose sources lead nowhere"
UNCITED = "Paragraphs under Events with no citation"
DATES = "Dates that don't match the cited row"
RECOLLECTION = "Memory-only facts not marked as memory"
SETUP = "Things that stopped a full check"
CATEGORY_ORDER = (NOWHERE_CITATIONS, NOWHERE_SOURCES, UNCITED, DATES, RECOLLECTION, SETUP)


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def relative(path, base):
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def replace_links(text):
    """Keep a link's ID or local file as a bracketed citation; else keep its label."""
    def swap(match):
        label, target = match.group(1), match.group(2).split("#")[0]
        if ID_RE.search(label):
            return f"[{label}]"
        if target and is_file_like(target):
            return f"[{target}]"
        return label

    return LINK_RE.sub(swap, text)


def is_file_like(token):
    if any(mark in token for mark in '"“”') or WEB_RE.search(token):
        return False
    return bool(FILE_EXT_RE.search(token)) or token.startswith(("./", "../", "/", "~/"))


def split_tokens(text):
    """Split on commas, semicolons and spaced slashes, but not inside quoted titles."""
    def protect(match):
        return match.group(0).replace(",", "\0").replace(";", "\1").replace("/", "\2")

    masked = QUOTED_RE.sub(protect, text)
    tokens = re.split(r"[,;]|\s/\s", masked)
    return [t.replace("\0", ",").replace("\1", ";").replace("\2", "/").strip() for t in tokens]


def parse_citation(text):
    citation = Citation()
    for raw in split_tokens(replace_links(text)):
        token = raw.strip(" \t`*[]()").strip()
        if len(token) > 1 and token[0] in "\"'" and token[-1] in "\"'":
            token = token[1:-1]
        if not token:
            continue
        if USER_PROVIDED_RE.match(token):
            citation.user_provided = True
        elif is_file_like(token.split("#")[0]):
            citation.files.append(token.split("#")[0])
        elif ID_RE.search(token):
            citation.ids.extend(ID_RE.findall(token))
        else:
            citation.words.append(token)
    return citation


def counts_as_citation(citation):
    if citation.ids or citation.files or citation.user_provided:
        return True
    for word in citation.words:
        has_date = bool(find_dates(word))
        date_only = has_date and not re.search(r"[A-Za-z]", re.sub(rf"{MONTH}", "", word))
        if (has_date and not date_only) or QUOTED_RE.search(word) or word.lower().startswith("exhibit"):
            return True
    return False


def file_exists(token, near, court):
    path = Path(unquote(token)).expanduser()
    if path.is_absolute():
        return path.exists()
    candidates = [near / path, court / path, court.parent / path]
    if path.parts and path.parts[0].lower() == "court":
        candidates.append(court.joinpath(*path.parts[1:]))
    return any(candidate.exists() for candidate in candidates)


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [cell.strip() for cell in cells]


def is_divider(cells):
    return bool(cells) and all(re.fullmatch(r":?-+:?", cell) for cell in cells)


def iter_tables(lines):
    """Yield (header cells, [(line number, row cells)]) for each Markdown table."""
    index = 0
    while index < len(lines):
        if lines[index].lstrip().startswith("|") and index + 1 < len(lines):
            header = split_row(lines[index])
            if is_divider(split_row(lines[index + 1])):
                rows = []
                index += 2
                while index < len(lines) and lines[index].lstrip().startswith("|"):
                    rows.append((index + 1, split_row(lines[index])))
                    index += 1
                yield [cell.lower() for cell in header], rows
                continue
        index += 1


def column(header, *names):
    for position, cell in enumerate(header):
        if any(cell.startswith(name) for name in names):
            return position
    return None


def cell_at(cells, position):
    return cells[position] if position is not None and position < len(cells) else ""


def parse_frontmatter(lines):
    if not lines or lines[0].strip() != "---":
        return {}, 0
    values = {}
    key = None
    for number, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return values, number + 1
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key:
            values[key] = ", ".join(filter(None, [values[key], item.group(1).strip()]))
            continue
        match = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if match:
            key = match.group(1)
            value = re.sub(r"\s+#.*$", "", match.group(2)).strip()
            values[key] = value[1:-1] if value[:1] in "\"'" and value[-1:] == value[:1] and len(value) > 1 else value
    return {}, 0


def check_sources(text, label, near, court, known, report):
    citation = parse_citation(text)
    for record_id in citation.ids:
        if record_id not in known:
            report.add(NOWHERE_SOURCES, f"{label} lists {record_id}, which isn't in the timeline or any entry.")
    for token in citation.files:
        if not file_exists(token, near, court):
            report.add(NOWHERE_SOURCES, f"{label} points to {token}, and that file doesn't exist.")
    report.to_read.extend(f"{label}: {word}" for word in citation.words)
    return citation


def load_timeline(court, report):
    path = court / "timeline.md"
    if not path.is_file():
        report.add(SETUP, f"No timeline.md in {court}. Build the timeline, or point me at the right folder.")
        return [], path, []
    lines = read_text(path).splitlines()
    records, source_cells = [], []
    for header, rows in iter_tables(lines):
        date_col = column(header, "date")
        source_col = column(header, "source")
        if date_col is None or source_col is None:
            continue
        precision_col = column(header, "precision")
        for line_number, cells in rows:
            match = ID_RE.fullmatch(cells[0].strip("*` ")) if cells else None
            if not match or not match.group(0).startswith("T-"):
                continue
            location = f"timeline.md line {line_number}"
            records.append(Record(
                match.group(0),
                cell_at(cells, date_col),
                cell_at(cells, precision_col).lower().strip("*` ") == "recollection",
                location,
            ))
            source_cells.append((match.group(0), location, cell_at(cells, source_col)))
    if not records:
        report.add(SETUP, "timeline.md has no rows I could read. Rows need a T-### ID plus Date and Sources columns.")
    return records, path, source_cells


def load_entries(court, report):
    records, documents = [], []
    for folder in ENTRY_FOLDERS:
        for path in sorted((court / folder).rglob("*.md")) if (court / folder).is_dir() else []:
            lines = read_text(path).splitlines()
            values, body_start = parse_frontmatter(lines)
            name = relative(path, court)
            record_id = values.get("event_id", "")
            if not re.fullmatch(r"(?:EVT|COM)-\d+", record_id):
                report.notes.append(f"{name} has no usable event_id, so nothing can cite it.")
                continue
            recollection = "recollection" in (
                values.get("date_precision", "").lower(), values.get("reliability", "").lower()
            )
            records.append(Record(record_id, values.get("date", ""), recollection, name))
            documents.append((record_id, path, name, values, lines[body_start:]))
    return records, documents


def check_folder(court, report):
    timeline, _, source_cells = load_timeline(court, report)
    entries, documents = load_entries(court, report)
    known = {}
    for record in timeline + entries:
        if record.record_id in known:
            report.add(SETUP, (
                f"{record.record_id} is used twice ({known[record.record_id].location} and "
                f"{record.location}), so a citation to it is ambiguous."
            ))
        else:
            known[record.record_id] = record

    for record_id, location, cell in source_cells:
        label = f"{record_id} ({location})"
        citation = check_sources(cell, label, court, court, known, report)
        if not (citation.ids or citation.files or citation.words or citation.user_provided):
            report.add(NOWHERE_SOURCES, f"{label} lists no source at all.")

    for record_id, path, name, values, body in documents:
        label = f"{record_id} ({name})"
        if values.get("source_file"):
            check_sources(values["source_file"], label, path.parent, court, known, report)
        for header, rows in iter_tables(body):
            position = column(header, "where it lives")
            for _, cells in rows if position is not None else []:
                if cell_at(cells, position):
                    check_sources(cell_at(cells, position), label, path.parent, court, known, report)
    return known


def clean_lines(text):
    """Blank frontmatter and code blocks, keeping line numbers right."""
    lines = text.splitlines()
    _, body_start = parse_frontmatter(lines)
    cleaned = [""] * body_start
    fenced = False
    for line in lines[body_start:]:
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            cleaned.append("")
        else:
            cleaned.append("" if fenced else line)
    return cleaned


def build_units(lines):
    """Split a document into paragraphs and list items; returns (units, found fact section)."""
    blocks = []
    current = None
    fact_level = None
    found_section = False
    section_number = 0

    for number, line in enumerate(lines, start=1):
        heading = HEADING_RE.match(line)
        stripped = line.strip()
        if heading:
            current = None
            section_number += 1
            level = len(heading.group(1))
            if fact_level is not None and level <= fact_level:
                fact_level = None
            if level >= 2 and FACT_SECTION_RE.match(re.sub(r"^[\W_]+", "", heading.group(2))):
                fact_level = level
                found_section = True
            continue
        if (not stripped or RULE_RE.match(line) or stripped.startswith("|")
                or stripped.startswith("<!--")):
            current = None
            continue
        if current is None or LIST_ITEM_RE.match(line):
            current = {
                "line": number,
                "parts": [],
                "fact": fact_level is not None,
                "section": section_number,
                "quote": stripped.startswith(">"),
            }
            blocks.append(current)
        current["parts"].append(re.sub(r"^\s*>\s?", "", LIST_ITEM_RE.sub("", line)).strip())

    units = []
    previous = None
    for block in blocks:
        text = " ".join(block["parts"])
        # A quote belongs to the paragraph that introduces it.
        if block["quote"] and previous is not None and previous["section"] == block["section"]:
            units[-1].text += " " + text
            continue
        units.append(Unit(block["line"], text, block["fact"]))
        previous = block
    return units, found_section


def excerpt(text, limit=70):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def split_citations(text):
    """Return (citations found in brackets, the wording with those brackets removed)."""
    citations = []

    def take(match):
        citation = parse_citation(match.group(1))
        if counts_as_citation(citation):
            citations.append(citation)
            return " "
        return match.group(0)

    prose = BRACKET_RE.sub(take, text)
    return citations, prose


def check_draft(path, court, known, report):
    lines = clean_lines(read_text(path))

    for number, line in enumerate(lines, start=1):
        for record_id in dict.fromkeys(ID_RE.findall(line)):
            if record_id not in known:
                report.add(NOWHERE_CITATIONS, f"Line {number}: {record_id} isn't in the timeline or any entry.")

    units, found_section = build_units(lines)
    if not found_section:
        report.add(SETUP, (
            "No Events section found, so paragraphs weren't checked for citations. "
            "Use a heading such as ## Events or ## Statement of facts."
        ))

    for unit in units:
        text = replace_links(unit.text)
        citations, prose = split_citations(text)

        if unit.in_fact_section and not citations:
            report.add(UNCITED, f'Line {unit.line}: "{excerpt(unit.text)}"')

        for citation in citations:
            for token in citation.files:
                if not file_exists(token, path.parent, court):
                    report.add(NOWHERE_CITATIONS, f"Line {unit.line}: {token} doesn't exist.")
            report.to_read.extend(f"Line {unit.line}: {word}" for word in citation.words)

        cited = [known[i] for i in dict.fromkeys(ID_RE.findall(text)) if i in known]
        if not cited:
            continue
        check_dates(unit, citations, prose, cited, report)
        check_recollection(unit, cited, report)


def check_dates(unit, citations, prose, cited, report):
    stated = find_dates(prose)
    if not stated:
        return
    allowed = [value for record in cited for _, value in find_dates(record.date_text)]
    allowed += [value for c in citations for word in c.words for _, value in find_dates(word)]
    if not allowed:
        names = ", ".join(record.record_id for record in cited)
        report.notes.append(f"Line {unit.line}: couldn't compare dates, because {names} has no readable date.")
        return
    for wording, value in stated:
        if not any(dates_match(value, other) for other in allowed):
            dated = "; ".join(f"{r.record_id} is dated {r.date_text or 'nothing'}" for r in cited)
            report.add(DATES, f'Line {unit.line}: says "{wording}", but {dated}.')


def check_recollection(unit, cited, report):
    if RECOLLECTION_PHRASE in " ".join(unit.text.lower().split()):
        return
    for record in cited:
        if record.recollection:
            report.add(RECOLLECTION, (
                f'Line {unit.line}: cites {record.record_id}, which comes from memory, '
                f'but doesn\'t say "to the best of my recollection".'
            ))


def print_report(draft, court, report):
    print(DISCLAIMER)
    print()
    print(f"Proof check of {draft}")
    print(f"Against court folder {court}")
    print()

    total = sum(len(messages) for messages in report.problems.values())
    for category in CATEGORY_ORDER:
        messages = report.problems.get(category)
        if messages:
            print(f"{category} ({len(messages)})")
            for message in messages:
                print(f"  - {message}")
            print()

    unique = list(dict.fromkeys(report.to_read))
    if unique:
        print(f"Sources described in words, which this script can't open ({len(unique)})")
        for item in unique[:MAX_TO_READ_SHOWN]:
            print(f"  - {item}")
        if len(unique) > MAX_TO_READ_SHOWN:
            print(f"  - and {len(unique) - MAX_TO_READ_SHOWN} more")
        print()

    if report.notes:
        print(f"Also worth a look ({len(report.notes)})")
        for note in report.notes:
            print(f"  - {note}")
        print()

    if total:
        print(f"Result: {total} problem(s) found. Nothing was changed.")
    else:
        print("Result: no problems found. Nothing was changed.")
    print("This only checks that citations line up. It doesn't check that the sources support the claims.")


class PlainParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"Proof check couldn't run: {message}", file=sys.stderr)
        raise SystemExit(1)


def main(argv=None):
    parser = PlainParser(description="Check a court narrative or packet against the court folder. Read-only.")
    parser.add_argument("draft", type=Path, help="the narrative or packet Markdown file")
    parser.add_argument("court", type=Path, help="the court folder")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    if not args.draft.is_file():
        parser.error(f"can't find the file {args.draft}")
    if not args.court.is_dir():
        parser.error(f"can't find the folder {args.court}")

    report = Report()
    known = check_folder(args.court, report)
    check_draft(args.draft, args.court, known, report)
    print_report(args.draft, args.court, report)
    return 1 if report.problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
