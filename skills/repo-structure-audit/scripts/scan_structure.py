#!/usr/bin/env python3
"""
scan_structure.py — read-only structural inventory of a repository.

Collects the facts a structure audit needs, deterministically, so the model spends its
effort on judgment instead of on walking the tree. Writes one JSON object to stdout.

This script never modifies, moves, or deletes anything in the target. Output must be a new
file outside the target. It does not follow symlinks out of the target and makes no network
calls. It reads entry points and small config candidates, and hashes same-size code, document,
and data files up to 256 KB to detect exact duplicates; file contents are never emitted.

Usage:
    python3 scan_structure.py TARGET [--max-depth 8] [--top 40] [--output FILE]

Python 3.8+. Standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------------------

# Directories whose contents are never interesting to a structure audit. We record that
# they exist and roughly how big they are, but we do not descend into them.
ARTIFACT_DIRS = {
    "node_modules": "dependencies",
    ".venv": "python-env",
    "venv": "python-env",
    "env": "python-env",
    "__pycache__": "python-cache",
    ".mypy_cache": "cache",
    ".pytest_cache": "cache",
    ".ruff_cache": "cache",
    ".tox": "cache",
    "dist": "build-output",
    "build": "build-output",
    "out": "build-output",
    ".next": "build-output",
    ".nuxt": "build-output",
    "target": "build-output",
    "coverage": "build-output",
    ".gradle": "build-output",
    ".terraform": "dependencies",
    "vendor": "dependencies",
    ".cache": "cache",
    ".parcel-cache": "cache",
    ".turbo": "cache",
}

# Never descended into, never reported as findings.
ALWAYS_SKIP = {".git", ".hg", ".svn", ".idea", ".vscode", ".DS_Store", ".Trash"}

# Nested checkouts — git worktrees, submodules, vendored clones. These are full duplicate
# copies of a tree. Walking into them doubles every count and manufactures duplicate-folder
# findings that do not exist. We record that they are there and stay out.
NESTED_CHECKOUT_DIRS = {".worktrees", "worktrees", ".submodules"}

# Files that legitimately live at repo root. Anything else loose at root is a candidate
# finding under P3 (smallest complete owner).
EXPECTED_ROOT_FILES = {
    "readme.md", "readme.rst", "readme.txt", "readme",
    "license", "license.md", "license.txt", "licence", "copying", "notice",
    "claude.md", "claude.local.md", "agents.md", "agent.md", "contributing.md",
    "changelog.md", "code_of_conduct.md", "security.md", "authors", "citation.cff",
    ".gitignore", ".gitattributes", ".editorconfig", ".gitmodules", ".mailmap",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
    "tsconfig.json", "jsconfig.json", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "requirements-dev.txt", "pipfile", "pipfile.lock", "poetry.lock",
    "uv.lock", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "gemfile", "gemfile.lock",
    "composer.json", "composer.lock", "pom.xml", "build.gradle", "build.gradle.kts",
    "settings.gradle", "makefile", "justfile", "taskfile.yml", "rakefile", "dockerfile",
    "docker-compose.yml", "docker-compose.yaml", ".dockerignore", ".env.example",
    ".env.sample", ".env.template", ".nvmrc", ".python-version", ".ruby-version",
    ".tool-versions", ".prettierrc", ".prettierignore", ".eslintrc", ".eslintrc.json",
    ".eslintrc.js", "eslint.config.js", ".babelrc", "babel.config.js", "jest.config.js",
    "vite.config.js", "vite.config.ts", "webpack.config.js", "rollup.config.js",
    "next.config.js", "tailwind.config.js", "postcss.config.js", "vitest.config.ts",
    ".pre-commit-config.yaml", "renovate.json", ".npmrc", ".yarnrc", "index.html",
}

# Files that mark a repository as a particular kind of thing.
PROFILE_MARKERS = {
    "software": [
        "package.json", "pyproject.toml", "setup.py", "go.mod", "Cargo.toml",
        "pom.xml", "build.gradle", "Gemfile", "composer.json", "requirements.txt",
        "Makefile", "CMakeLists.txt", "mix.exs", "build.sbt",
    ],
    "ai_workspace": ["CLAUDE.md", "AGENTS.md", "CLAUDE.local.md", ".claude", ".cursor"],
    "infra": ["main.tf", "Chart.yaml", "kustomization.yaml", "ansible.cfg", "Pulumi.yaml"],
}

CODE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb", ".java", ".kt", ".swift",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".scala", ".ex", ".exs", ".sh", ".bash",
    ".zsh", ".fish", ".ps1", ".sql", ".vue", ".svelte", ".r", ".jl", ".lua", ".pl",
}
DOC_EXTS = {".md", ".rst", ".txt", ".org", ".adoc", ".pdf", ".docx", ".doc", ".rtf"}
DATA_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".csv", ".tsv", ".xml", ".parquet"}
MEDIA_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mov", ".mp3", ".wav",
              ".webp", ".heic", ".pptx", ".xlsx", ".key", ".psd", ".ai", ".fig"}

# Credential detection, split by confidence.
#
# HARD patterns are credential-bearing by their very name — flag them whatever the
# extension. SOFT patterns are name *hints* ("token", "secret", "credentials") that appear
# constantly in ordinary source and docs: `check-linkedin-token.py` is a script that checks
# a token, not a token. Flagging those trains the reader to ignore the section, which is
# exactly what you cannot afford in the one part of the report that must be believed.
SECRET_PATTERNS_HARD = [
    re.compile(r"^\.env$"),
    re.compile(r"^\.env\.(?!example$|sample$|template$|local\.example$)"),
    re.compile(r"\.pem$"), re.compile(r"\.p12$"), re.compile(r"\.pfx$"),
    re.compile(r"^id_(rsa|dsa|ecdsa|ed25519)$"),
    re.compile(r"\.kdbx$"), re.compile(r"\.keystore$"), re.compile(r"\.jks$"),
    re.compile(r"service[-_]?account.*\.json$", re.I),
    re.compile(r"^\..*(token|credential|secret)s?.*\.json$", re.I),  # dotfile caches
]
SECRET_PATTERNS_SOFT = [
    re.compile(r"(^|[-_.])credentials?([-_.]|$)", re.I),
    re.compile(r"(^|[-_.])secrets?([-_.]|$)", re.I),
    re.compile(r"client[-_]?secret", re.I),
    re.compile(r"(^|[-_.])token[s]?([-_.]|$)", re.I),
    re.compile(r"(^|[-_.])api[-_]?keys?([-_.]|$)", re.I),
]
# A soft hint inside a source, markup, or documentation file is describing credentials,
# not holding them.
SECRET_SOFT_EXCLUDE_EXTS = CODE_EXTS | DOC_EXTS | {".html", ".htm", ".css", ".lock", ".log"}
SECRET_SAFE = re.compile(r"(example|sample|template|test|fixture|mock|dummy|placeholder)",
                         re.I)

# Config-as-prose candidates: prose files whose *name* suggests they hold values.
CONFIG_NAME_HINT = re.compile(
    r"(config|settings|params|parameters|options|thresholds|rules|constants|"
    r"endpoints|registry|manifest|schedule|guardrails)", re.I
)

# Files a config-shaped directory would be expected to contain.
MACHINE_CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".properties", ".env"}

ARCHIVE_HINT = re.compile(r"^_?(archive|archived|old|deprecated|retired|legacy|attic|"
                          r"backup|bak|previous|superseded|obsolete)s?$", re.I)
# Fully anchored: a scratch name is the whole name, optionally numbered or suffixed.
# `test`/`tests` is deliberately absent — it is the standard test directory in most
# ecosystems, and calling someone's test folder disposable discredits the whole report.
SCRATCH_HINT = re.compile(r"^(_?tmp|_?temp|scratch(pad)?|junk|misc|untitled|new folder|"
                          r"stuff|foo|bar|delete[-_]?me|wip)\d*([-_ .].*)?$", re.I)
AUDIT_HINT = re.compile(r"^(audits?|reports?|reviews?|assessments?)$", re.I)
GENERATED_REPORT = re.compile(
    r"^(STRUCTURE-AUDIT|RESTRUCTURE-PLAN)-\d{4}-\d{2}-\d{2}(?:-\d+)?\.md$",
    re.I,
)
AMBIGUOUS_ARTIFACT_DIRS = {"vendor", "env", "out", "build", "target"}
SENTINEL_FILES = {".gitkeep", ".keep"}

# Filenames that are *supposed* to repeat all over a tree — one per package, one per
# module. Reporting these as duplication is noise, not a finding.
UBIQUITOUS_FILENAMES = {
    "README.md", "readme.md", "CLAUDE.md", "AGENTS.md", "SKILL.md", "LICENSE",
    "CHANGELOG.md", "TODO.md", "package.json", "package-lock.json", "tsconfig.json",
    "pyproject.toml", "setup.py", "requirements.txt", "go.mod", "go.sum", "Cargo.toml",
    "Gemfile", "composer.json", "Makefile", "Dockerfile", ".gitignore", ".gitkeep",
    ".DS_Store", "__init__.py", "conftest.py", "index.ts", "index.js", "index.tsx",
    "index.jsx", "index.html", "main.py", "main.go", "mod.rs", "lib.rs", "types.ts",
    "utils.ts", "constants.ts", "styles.css",
}
# Content hashing is capped so the scan stays fast on repos with large binaries.
DUP_HASH_MAX_BYTES = 256 * 1024
DUP_HASH_EXTS = CODE_EXTS | DOC_EXTS | DATA_EXTS
# Caches and generated trees are *supposed* to hold repeated content. Hashing them is
# both slow and pure noise.
DUP_SKIP_SEGMENT = re.compile(r"^(cache|caches|\.cache|node_modules|vendor|venv|\.venv|"
                              r"dist|build|out|target|coverage|__pycache__|"
                              r"\.next|\.nuxt|\.pytest_cache|\.mypy_cache)$", re.I)
# A name repeated a handful of times is a stray copy worth looking at. A name repeated
# twenty times is a naming pattern across per-instance folders — reporting it as
# duplication is the single noisiest thing a structure scanner can do.
DUP_MAX_GROUP = 4
# Spelled out in the JSON so a reader of the raw output cannot mistake the bucket for a
# fourth naming convention and count it. `distinct_styles` already excludes it.
NUMERIC_STYLE = "numeric (hierarchy, not a style — excluded from distinct_styles)"
DATED_FILE = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{8}|\d{4}_\d{2}_\d{2}|\d{2}-\d{2}-\d{4})")

# Suffixes stripped when looking for near-duplicate folder names.
DUP_SUFFIX = re.compile(
    r"(v\d+|version\d+|\d+|copy|final|new|old|latest|draft|backup|bak|results?|"
    r"output|out|updated|revised)$"
)


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def classify_name_style(name):
    """Which naming convention does this directory name follow?"""
    # Year, date, and numeric folders are a hierarchy, not a naming convention. Counting
    # them as a style inflates the style count and points the audit at the one part of
    # the tree that is usually organized correctly.
    if re.fullmatch(r"[\d._-]+", name):
        return NUMERIC_STYLE
    if " " in name:
        return "spaced"
    has_upper = any(c.isupper() for c in name)
    has_lower = any(c.islower() for c in name)
    if "-" in name and "_" in name:
        return "mixed-separators"
    if "-" in name:
        return "Kebab-Mixed-Case" if has_upper else "kebab-case"
    if "_" in name:
        if name.startswith("_"):
            # A single leading underscore is a widely used "meta/aside" marker, not a
            # separate convention. Judge by what follows it.
            return classify_name_style(name.lstrip("_")) if name.lstrip("_") else "other"
        return "SNAKE_UPPER" if not has_lower else "snake_case"
    if has_upper and has_lower:
        return "PascalOrCamelCase"
    if has_upper:
        return "UPPERCASE"
    if has_lower:
        return "lowercase"
    return "other"


def dup_key(name):
    """Normalize a folder name so near-duplicates collide."""
    k = name.lower().strip()
    k = re.sub(r"[\s\-_.]+", "", k)
    prev = None
    while prev != k:  # strip stacked suffixes: "thing-v2-final" -> "thing"
        prev = k
        k = DUP_SUFFIX.sub("", k)
    return k


def secret_confidence(name):
    """Return 'high', 'low', or None for how likely this filename holds a credential."""
    if any(p.search(name) for p in SECRET_PATTERNS_HARD):
        return None if SECRET_SAFE.search(name) else "high"
    if SECRET_SAFE.search(name):
        return None
    ext = Path(name).suffix.lower()
    if ext in SECRET_SOFT_EXCLUDE_EXTS:
        return None
    if any(p.search(name) for p in SECRET_PATTERNS_SOFT):
        return "low"
    return None


def safe_stat(path):
    try:
        return path.stat()
    except (OSError, ValueError):
        return None


def word_count(path, limit_bytes=400_000):
    try:
        if path.stat().st_size > limit_bytes:
            return None
        return len(path.read_text(encoding="utf-8", errors="ignore").split())
    except (OSError, ValueError):
        return None


def run_git(root, args, timeout=30):
    """Run a git command. Returns stdout as a string, or None if git is unavailable."""
    try:
        r = subprocess.run(
            ["git", "-C", str(root)] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def git_path_ignored(root, relative_path, timeout=30):
    """Use Git's own matcher for ignore semantics."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "--no-index", "--quiet", "--",
             str(relative_path)],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def dir_size_bounded(path, max_entries=6000):
    """Approximate directory size without walking forever. Returns (bytes, capped)."""
    total, seen = 0, 0
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    seen += 1
                    if seen > max_entries:
                        return total, True
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return total, False


def human_size(n):
    units = ["B", "KB", "MB", "GB", "TB"]
    i, v = 0, float(n)
    while v >= 1024 and i < len(units) - 1:
        v /= 1024
        i += 1
    return f"{v:.1f}{units[i]}" if i else f"{int(v)}B"


# --------------------------------------------------------------------------------------
# Scanner
# --------------------------------------------------------------------------------------

class Scanner:
    def __init__(self, root, max_depth=8, top=40):
        self.root = Path(root).resolve()
        self.max_depth = max_depth
        self.top = top

        self.dirs = []              # per-directory records
        self.artifact_dirs = []
        self.nested_checkouts = []
        self.basenames = set()      # every filename seen, for resolving bare references
        self.name_index = defaultdict(list)   # basename -> paths, for cross-folder copies
        self.size_index = defaultdict(list)   # size -> paths, hashed later on collision
        self.empty_dirs = []
        self.zero_byte_files = []
        self.sentinel_files = []
        self.secret_candidates = []
        self.config_prose_candidates = []
        self.archive_dirs = []
        self.scratch_dirs = []
        self.audit_dirs = []
        self.dated_files = 0
        self.date_formats = Counter()
        self.ext_counter = Counter()
        self.mtime_dates = Counter()
        self.file_count = 0
        self.total_bytes = 0
        self.deepest = 0
        self.skipped_unreadable = []
        self.pruned_directories = []
        self.generated_reports_excluded = 0

    # -- walk ---------------------------------------------------------------------------

    def walk(self):
        self._walk_dir(self.root, depth=0)

    def _walk_dir(self, path, depth):
        self.deepest = max(self.deepest, depth)
        try:
            entries = sorted(os.scandir(path), key=lambda e: e.name)
        except OSError as e:
            self.skipped_unreadable.append({"path": self._rel(path), "error": e.strerror})
            return

        n_files = n_dirs = ignored_files = 0
        child_files = []

        for entry in entries:
            name = entry.name
            if name in ALWAYS_SKIP:
                continue
            try:
                is_dir = entry.is_dir(follow_symlinks=False)
                is_file = entry.is_file(follow_symlinks=False)
            except OSError:
                continue

            if is_dir:
                n_dirs += 1
                # A nested checkout is a duplicate of some other tree. Note it, stay out.
                if name in NESTED_CHECKOUT_DIRS or (
                    depth > 0 and (Path(entry.path) / ".git").exists()
                ):
                    self.nested_checkouts.append({
                        "path": self._rel(Path(entry.path)),
                        "reason": ("known worktree/submodule directory"
                                   if name in NESTED_CHECKOUT_DIRS
                                   else "contains its own .git"),
                    })
                    continue
                if name in ARTIFACT_DIRS:
                    size, capped = dir_size_bounded(Path(entry.path))
                    self.artifact_dirs.append({
                        "path": self._rel(Path(entry.path)),
                        "kind": ARTIFACT_DIRS[name],
                        "name": name,
                        "size_bytes": size,
                        "size_human": ("≥" if capped else "") + human_size(size),
                        "size_is_lower_bound": capped,
                        "parent_last_modified": self._parent_mtime(Path(entry.path)),
                        "requires_confirmation": name in AMBIGUOUS_ARTIFACT_DIRS,
                    })
                    continue  # never descend into artifact directories
                if ARCHIVE_HINT.match(name):
                    self.archive_dirs.append(self._rel(Path(entry.path)))
                if SCRATCH_HINT.match(name):
                    self.scratch_dirs.append(self._rel(Path(entry.path)))
                if AUDIT_HINT.match(name):
                    self.audit_dirs.append(self._rel(Path(entry.path)))
                if depth < self.max_depth:
                    self._walk_dir(Path(entry.path), depth + 1)
                else:
                    self.pruned_directories.append(self._rel(Path(entry.path)))

            elif is_file:
                if GENERATED_REPORT.match(name):
                    ignored_files += 1
                    self.generated_reports_excluded += 1
                    continue
                n_files += 1
                self.file_count += 1
                child_files.append(name)
                self._record_file(Path(entry.path), name)

        rec = {
            "path": self._rel(path),
            "depth": depth,
            "n_files": n_files,
            "n_subdirs": n_dirs,
            "name": path.name or ".",
            "n_ignored_files": ignored_files,
        }
        if n_files == 0 and n_dirs == 0 and ignored_files == 0:
            self.empty_dirs.append(rec["path"])
        if n_files == 1 and n_dirs == 0:
            rec["only_file"] = child_files[0]
        self.dirs.append(rec)

    def _record_file(self, path, name):
        self.basenames.add(name)
        st = safe_stat(path)
        if st:
            self.total_bytes += st.st_size
            if st.st_size == 0:
                if name in SENTINEL_FILES:
                    self.sentinel_files.append(self._rel(path))
                else:
                    self.zero_byte_files.append(self._rel(path))
            # Indexes behind the two file-level duplication checks. Sizes are recorded now
            # and hashed later only where they collide, so a repo with no duplicates pays
            # nothing beyond the stat it was already doing.
            rel = self._rel(path)
            if not any(DUP_SKIP_SEGMENT.match(seg) for seg in Path(rel).parts[:-1]):
                if name not in UBIQUITOUS_FILENAMES:
                    self.name_index[name].append(rel)
                if (0 < st.st_size <= DUP_HASH_MAX_BYTES
                        and path.suffix.lower() in DUP_HASH_EXTS):
                    self.size_index[st.st_size].append(rel)
            try:
                d = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).date().isoformat()
                self.mtime_dates[d] += 1
            except (OSError, OverflowError, ValueError):
                pass

        ext = path.suffix.lower()
        self.ext_counter[ext or "(none)"] += 1

        conf = secret_confidence(name)
        if conf:
            self.secret_candidates.append({
                "path": self._rel(path),
                "name": name,
                "confidence": conf,
                "size_bytes": st.st_size if st else None,
            })

        if ext in {".md", ".txt", ".rst"} and CONFIG_NAME_HINT.search(name):
            self.config_prose_candidates.append({
                "path": self._rel(path),
                "word_count": word_count(path),
                "reason": "prose file whose name suggests it holds values",
            })

        m = DATED_FILE.search(name)
        if m:
            self.dated_files += 1
            token = m.group(1)
            if re.match(r"^\d{4}-\d{2}-\d{2}$", token):
                self.date_formats["YYYY-MM-DD"] += 1
            elif re.match(r"^\d{8}$", token):
                self.date_formats["YYYYMMDD"] += 1
            elif re.match(r"^\d{4}_\d{2}_\d{2}$", token):
                self.date_formats["YYYY_MM_DD"] += 1
            else:
                self.date_formats["DD-MM-YYYY or ambiguous"] += 1

    def _rel(self, path):
        try:
            r = str(Path(path).resolve().relative_to(self.root))
        except ValueError:
            return str(path)
        return "." if r == "." else r

    def _parent_mtime(self, path):
        st = safe_stat(path.parent)
        if not st:
            return None
        try:
            return datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).date().isoformat()
        except (OSError, OverflowError, ValueError):
            return None

    # -- derived facts ------------------------------------------------------------------

    def root_inventory(self):
        """What sits at the top level, split into folders, expected files, and loose files."""
        folders, expected, loose = [], [], []
        try:
            entries = sorted(os.scandir(self.root), key=lambda e: e.name)
        except OSError:
            return {"folders": [], "expected_files": [], "loose_files": []}

        for entry in entries:
            name = entry.name
            if name in ALWAYS_SKIP:
                continue
            try:
                if entry.is_dir(follow_symlinks=False):
                    folders.append(name)
                    continue
                if not entry.is_file(follow_symlinks=False):
                    continue
            except OSError:
                continue

            if GENERATED_REPORT.match(name):
                continue

            st = safe_stat(Path(entry.path))
            info = {
                "name": name,
                "ext": Path(name).suffix.lower() or "(none)",
                "size_bytes": st.st_size if st else None,
            }
            if name.lower() in EXPECTED_ROOT_FILES or name.lower().startswith(".env.example"):
                expected.append(name)
            else:
                info["likely_role"] = self._guess_role(name)
                loose.append(info)

        return {"folders": folders, "expected_files": expected, "loose_files": loose}

    @staticmethod
    def _guess_role(name):
        ext = Path(name).suffix.lower()
        if ext in MEDIA_EXTS:
            return "media or reusable asset"
        if ext in CODE_EXTS:
            return "source code"
        if ext in {".json", ".csv", ".tsv", ".xml", ".parquet"}:
            return "data export or scratch output"
        if ext in {".yaml", ".yml", ".toml", ".ini"}:
            return "configuration"
        if ext in DOC_EXTS:
            return "document"
        if ext in {".zip", ".tar", ".gz", ".tgz", ".dmg", ".pkg"}:
            return "archive or download"
        return "unknown"

    def entry_points(self):
        found = []
        candidates = ("README.md", "README.rst", "README.txt", "README",
                      "CLAUDE.md", "AGENTS.md", "CLAUDE.local.md", "index.md")
        for candidate in candidates:
            p = self.root / candidate
            if p.is_file():
                found.append(self._entry_point_record(p, "root"))

        for directory in self.dirs:
            if directory["path"] == "." or directory["depth"] > 3:
                continue
            base = self.root / directory["path"]
            if not self._looks_like_project_root(base):
                continue
            for candidate in candidates:
                p = base / candidate
                if p.is_file():
                    found.append(self._entry_point_record(p, "project"))
        found.sort(key=lambda item: (item["scope"] != "root", item["path"]))
        return found

    def _entry_point_record(self, path, scope):
        wc = word_count(path)
        return {
            "name": path.name,
            "path": self._rel(path),
            "scope": scope,
            "word_count": wc,
            "substantive": bool(wc and wc >= 100),
            "referenced_paths": self._extract_paths(path),
        }

    @staticmethod
    def _looks_like_project_root(base):
        markers = {m for values in PROFILE_MARKERS.values() for m in values}
        if any((base / marker).exists() for marker in markers):
            return True
        return any((base / name).is_dir() for name in
                   ("src", "tests", "test", "scripts", "lib", "app", "config"))

    def _extract_paths(self, path, cap=120):
        """Pull path-looking strings out of an entry point and check whether they exist.

        A router pointing at a missing path is one of the highest-value findings available,
        and it is purely mechanical to detect — so the scanner does it rather than making
        the model read and cross-check by hand.
        """
        try:
            if path.stat().st_size > 400_000:
                return {"note": "file too large to parse", "checked": 0}
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return {"note": "unreadable", "checked": 0}

        found = set()
        # Markdown links, backticked paths, and bare path-like tokens. The lookbehind
        # excludes `/`, `.`, and `-` so we do not re-match a fragment of a path we already
        # captured — without it, `docs/direction/NEXT-STEPS.md` also yields the bogus
        # sub-path `direction/NEXT-STEPS.md`, which then reports as missing.
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            found.add(m.group(1))
        for m in re.finditer(r"`([^`\n]{2,120})`", text):
            found.add(m.group(1))
        for m in re.finditer(r"(?<![\w`(/.\-])((?:\./|~/)?[\w.\-]+/[\w./\-]+)", text):
            found.add(m.group(1))

        missing, outside_target, existing, skipped_placeholder = [], [], 0, 0
        for raw in sorted(found)[:cap * 4]:
            c = raw.strip().strip("`\"'").split("#")[0].split("?")[0]
            if not c or c.startswith(("http://", "https://", "mailto:")):
                continue
            if " " in c:
                continue
            if c.startswith("~/"):
                outside_target.append(c)
                continue
            # Placeholders and naming templates are not claims that a file exists.
            if re.search(r"[<>{}*$]|YYYY|MM-DD|\bNNN\b|\.\.\.", c):
                skipped_placeholder += 1
                continue
            c = c[2:] if c.startswith("./") else c
            normalized = c

            if "/" not in c:
                # A bare filename means "a file called this", not "./this". Resolve it
                # against every basename in the tree before calling it missing.
                if not re.search(r"\.\w{1,5}$", c):
                    continue
                gone = c not in self.basenames
            else:
                try:
                    if c.startswith("/"):
                        candidate = (self.root / c.lstrip("/")).resolve()
                    else:
                        candidate = (path.parent / c.rstrip("/")).resolve()
                    try:
                        relative = candidate.relative_to(self.root)
                    except ValueError:
                        outside_target.append(c)
                        continue
                    normalized = str(relative)
                    if candidate.exists():
                        gone = False
                    elif re.search(r"\.\w{1,5}$", c) or c.endswith("/"):
                        gone = True
                    else:
                        continue
                except (OSError, ValueError):
                    continue

            if gone:
                missing.append({"path": normalized, "context": self._context_for(text, raw)})
            else:
                existing += 1
            if len(missing) >= cap:
                break

        # A document that says "never create tmp/" is not claiming tmp/ exists. The
        # scanner cannot resolve intent, so it hands the surrounding sentence to the model
        # along with a cheap negation flag rather than reporting a confident false positive.
        for m in missing:
            m["looks_like_prohibition"] = bool(re.search(
                r"\b(never|don't|do not|avoid|no longer|deprecated|instead of|"
                r"rather than|not to|forbidden|prohibited)\b", m["context"], re.I))

        prohibitions = sorted(
            (item for item in missing if item["looks_like_prohibition"]),
            key=lambda item: item["path"],
        )
        missing = sorted(
            (item for item in missing if not item["looks_like_prohibition"]),
            key=lambda item: item["path"],
        )
        return {"checked": existing + len(missing) + len(prohibitions), "resolved": existing,
                "missing": missing[:self.top],
                "prohibitions": prohibitions[:self.top],
                "outside_target": sorted(set(outside_target))[:self.top],
                "placeholders_ignored": skipped_placeholder,
                "note": "Missing contains unresolved in-target paths. Prohibitions contains "
                        "path-like rules about what must not exist. Outside_target contains "
                        "boundaries that were not resolved silently."}

    @staticmethod
    def _context_for(text, token, window=90):
        i = text.find(token)
        if i < 0:
            return ""
        return " ".join(text[max(0, i - window):i + len(token) + window].split())

    def naming(self):
        styles = Counter()
        by_style = defaultdict(list)
        for d in self.dirs:
            if d["path"] == ".":
                continue
            name = d["name"]
            s = classify_name_style(name)
            styles[s] += 1
            if len(by_style[s]) < 12:
                by_style[s].append(d["path"])
        return {
            "directory_styles": dict(styles.most_common()),
            "examples_by_style": {k: v for k, v in by_style.items()},
            "distinct_styles": len([s for s in styles if s != NUMERIC_STYLE]),
            "dated_files": self.dated_files,
            "date_formats": dict(self.date_formats),
        }

    def duplicates(self):
        """Find *real* duplication, not folders that legitimately repeat per project.

        Five `config/` folders in five projects is correct structure — each project owns
        its own. Reporting that as duplication is the fastest way to make an audit feel
        wrong. Only three shapes are genuine signals:

          siblings        two folders in the SAME parent describing the same thing
          active_archive  the same thing present in both an active and an archived location
          separator_only  the same name in two naming styles (email_triage / email-triage)
        """
        groups = defaultdict(list)
        for d in self.dirs:
            if d["path"] == "." or not d["name"]:
                continue
            k = dup_key(d["name"])
            if len(k) < 3:
                continue
            groups[k].append(d["path"])

        def archived(p):
            return any(ARCHIVE_HINT.match(seg) for seg in Path(p).parts)

        siblings, active_archive, separator_only = [], [], []
        for k, paths in groups.items():
            if len(paths) < 2:
                continue
            names = {Path(p).name for p in paths}

            by_parent = defaultdict(list)
            for p in paths:
                by_parent[str(Path(p).parent)].append(p)
            for parent, group in by_parent.items():
                if len(group) > 1 and len({Path(g).name for g in group}) > 1:
                    siblings.append({"normalized": k, "parent": parent,
                                     "paths": sorted(group)[:6]})

            # A genuine active/archive duplicate is the SAME item in both places: strip the
            # archive segment and the two paths coincide. Without this test, every
            # per-instance subfolder (each job application having a receipts/ folder, some
            # of those applications being archived) reads as a duplicate.
            live_set = {p for p in paths if not archived(p)}
            for p in paths:
                if not archived(p):
                    continue
                stripped = "/".join(seg for seg in Path(p).parts
                                    if not ARCHIVE_HINT.match(seg))
                if stripped in live_set:
                    active_archive.append({"normalized": k, "active": stripped,
                                           "archived": p})

            if len(names) > 1:
                styles = {classify_name_style(n.lstrip("_")) for n in names}
                collapsed = {re.sub(r"[\-_]", "", n).lower() for n in names}
                if len(collapsed) == 1 and len(styles) > 1:
                    separator_only.append({"names": sorted(names),
                                           "paths": sorted(paths)[:6]})

        return {
            "sibling_near_duplicates": siblings[:self.top],
            "active_and_archived_copies": active_archive[:self.top],
            "separator_style_variants": separator_only[:self.top],
            "same_name_across_folders": self._same_name_files(),
            "identical_content_files": self._identical_content(),
            "note": "Same-named folders in different projects are deliberately excluded — "
                    "per-project config/, docs/, or tests/ folders are correct structure, "
                    "not duplication. The same rule applies to files: a repeated name is "
                    "only reported when the parent folders differ in name too.",
        }

    def _same_name_files(self):
        """The same filename in two differently-named folders.

        This is the commonest duplication in a documents repo and the folder-level checks
        cannot see it. The parent-name test is what keeps it quiet: two `app.yaml` files
        under two `config/` folders are per-project structure, while `q1-report.md` in
        `Final Reports/` and in `exports/` is one document living in two places.
        """
        out = []
        for name, paths in self.name_index.items():
            if not 2 <= len(paths) <= DUP_MAX_GROUP:
                continue
            parents = {Path(p).parent.name for p in paths}
            if len(parents) < 2:
                continue
            out.append({"filename": name, "paths": sorted(paths)[:6],
                        "count": len(paths)})
        out.sort(key=lambda r: -r["count"])
        return out[:self.top]

    def _identical_content(self):
        """Byte-identical files anywhere in the tree, whatever they are named.

        Catches the case no name-based check can: one helper copy-pasted into three
        packages under three different filenames. Only size collisions are hashed, so
        this costs nothing on a repo that has no duplicates.
        """
        out = []
        for size, paths in self.size_index.items():
            # A size shared by a crowd of files is a generated pattern, not a copy-paste.
            # Skipping those buckets is also what keeps this fast on a large repo.
            if not 2 <= len(paths) <= 12:
                continue
            by_digest = defaultdict(list)
            for rel in paths:
                try:
                    with open(self.root / rel, "rb") as fh:
                        by_digest[hashlib.sha1(fh.read()).hexdigest()].append(rel)
                except OSError:
                    continue
            for digest, group in by_digest.items():
                if 1 < len(group) <= DUP_MAX_GROUP:
                    out.append({"paths": sorted(group)[:6], "count": len(group),
                                "size_bytes": size, "sha1": digest[:12]})
        out.sort(key=lambda r: (-r["count"], -r["size_bytes"]))
        return out[:self.top]

    def profile_signals(self):
        signals = {k: [] for k in PROFILE_MARKERS}
        for kind, markers in PROFILE_MARKERS.items():
            for m in markers:
                if (self.root / m).exists():
                    signals[kind].append(m)
        # Markers can also live one level down (a projects/ or packages/ layout).
        nested = defaultdict(int)
        for d in self.dirs:
            if d["depth"] not in (1, 2):
                continue
            for kind, markers in PROFILE_MARKERS.items():
                for m in markers:
                    if (self.root / d["path"] / m).exists():
                        nested[kind] += 1
        code = sum(self.ext_counter[e] for e in CODE_EXTS if e in self.ext_counter)
        docs = sum(self.ext_counter[e] for e in DOC_EXTS if e in self.ext_counter)
        data = sum(self.ext_counter[e] for e in DATA_EXTS if e in self.ext_counter)
        media = sum(self.ext_counter[e] for e in MEDIA_EXTS if e in self.ext_counter)
        return {
            "root_markers": {k: v for k, v in signals.items() if v},
            "nested_marker_counts": dict(nested),
            "file_mix": {"code": code, "docs": docs, "data": data, "media": media,
                         "other": max(0, self.file_count - code - docs - data - media)},
        }

    def layout_candidates(self):
        """Directories that look like project roots, and how they lay out src/tests/scripts."""
        out = []
        for d in self.dirs:
            # The root is included deliberately: on a single-project repo it is the only
            # project there is, and skipping it meant `colocated_tests` — the guardrail
            # against flagging JS/TS tests that sit beside their source — never fired.
            if d["depth"] > 3:
                continue
            base = self.root / d["path"]
            present = [x for x in ("src", "tests", "test", "scripts", "lib", "app",
                                   "docs", "config", "assets", "output", "bin")
                       if (base / x).is_dir()]
            markers = [m for ms in PROFILE_MARKERS.values() for m in ms if (base / m).exists()]
            entry = [f for f in ("README.md", "CLAUDE.md", "AGENTS.md")
                     if (base / f).is_file()]
            if not (present or markers):
                continue
            colocated = self._has_colocated_tests(base / "src") if (base / "src").is_dir() else False
            out.append({
                "path": d["path"],
                "standard_dirs": present,
                "manifest_files": markers,
                "entry_point": entry,
                "n_files": d["n_files"],
                "n_subdirs": d["n_subdirs"],
                "empty_standard_dirs": [x for x in present if self._is_empty(base / x)],
                "colocated_tests": colocated,
                "is_root": d["depth"] == 0,
            })
        out.sort(key=lambda item: (not item["is_root"], item["path"]))
        return out[:self.top]

    @staticmethod
    def _is_empty(path):
        try:
            return not any(path.iterdir())
        except OSError:
            return False

    @staticmethod
    def _has_colocated_tests(src, max_entries=5000):
        """JS/TS repos legitimately put tests beside source. Detect so we never flag it."""
        count = seen = 0
        for current, dirnames, filenames in os.walk(src):
            dirnames[:] = [name for name in dirnames
                           if name not in ARTIFACT_DIRS and name not in ALWAYS_SKIP]
            for filename in filenames:
                seen += 1
                if seen > max_entries:
                    return False
                if re.search(r"\.(test|spec)\.[jt]sx?$", filename):
                    count += 1
                    if count >= 2:
                        return True
        return False

    def config_landscape(self):
        machine, prose_dirs = [], []
        for d in self.dirs:
            base = self.root / d["path"]
            if d["name"].lower() in {"config", "configs", "conf", "settings"}:
                try:
                    files = [f.name for f in base.iterdir() if f.is_file()]
                except OSError:
                    files = []
                mach = [f for f in files if Path(f).suffix.lower() in MACHINE_CONFIG_EXTS]
                prose = [f for f in files if Path(f).suffix.lower() in {".md", ".txt", ".rst"}]
                prose_dirs.append({"path": d["path"], "machine_readable": mach,
                                   "prose": prose})
        for ext in MACHINE_CONFIG_EXTS:
            machine.append({"ext": ext, "count": self.ext_counter.get(ext, 0)})
        return {
            "config_dirs": prose_dirs,
            "machine_config_counts": {m["ext"]: m["count"] for m in machine if m["count"]},
            "prose_config_candidates": self.config_prose_candidates[:self.top],
        }

    def mtime_analysis(self):
        """Detect the mtime clustering that makes file dates useless as a freshness signal."""
        if not self.mtime_dates:
            return {"usable": False, "reason": "no readable modification times"}
        total = sum(self.mtime_dates.values())
        top_date, top_n = self.mtime_dates.most_common(1)[0]
        share = top_n / total if total else 0
        # Two ways dates become useless: a big repo where a clone or bulk commit stamped a
        # large slice at once, or any repo where nearly every file shares one date. The
        # second case is what a fresh copy or a sync tool leaves behind, and without it a
        # small repo reports its dates as trustworthy when they carry no information.
        clustered = (share > 0.30 and top_n >= 20) or (share >= 0.90 and total >= 3)
        recent = sorted(self.mtime_dates.items(), reverse=True)[:1]
        return {
            "usable": not clustered,
            "clustered": clustered,
            "cluster_date": top_date if clustered else None,
            "cluster_share": round(share, 3),
            "warning": (
                "More than 30% of files share one modification date. A clone, checkout, bulk "
                "commit, or cloud-sync tool probably touched everything at once — do not use "
                "mtime to judge staleness in this repo. Use content dates, dated filenames, "
                "or git log instead."
            ) if clustered else None,
            "newest_file_date": recent[0][0] if recent else None,
            "distinct_days": len(self.mtime_dates),
        }

    def git_facts(self):
        git_root_raw = run_git(self.root, ["rev-parse", "--show-toplevel"])
        if not git_root_raw:
            return {"is_git_repo": False,
                    "note": "No version control: no history, no rollback, and no ignore "
                            "layer for the day this becomes a repo."}
        git_root = Path(git_root_raw.strip()).resolve()
        facts = {
            "is_git_repo": True,
            "repository_root": str(git_root),
            "scope": "root" if git_root == self.root else "subdirectory",
        }
        tracked_raw = run_git(self.root, ["ls-files", "-z", "--", "."])
        tracked = set(tracked_raw.split("\0")) if tracked_raw else set()
        tracked.discard("")
        facts["tracked_file_count"] = len(tracked)

        log = run_git(self.root, ["log", "-1", "--format=%cI|%h|%an", "--", "."])
        if log and log.strip():
            iso, sha, author = (log.strip().split("|") + ["", "", ""])[:3]
            facts["last_commit"] = {"date": iso, "sha": sha, "author": author}
        count_raw = run_git(self.root, ["rev-list", "--count", "HEAD"])
        try:
            facts["commit_count"] = int((count_raw or "0").strip() or "0")
        except ValueError:
            facts["commit_count"] = 0

        status = run_git(self.root, ["status", "--porcelain"])
        if status is not None:
            lines = [l for l in status.splitlines() if l.strip()]
            facts["uncommitted_changes"] = len(lines)
            facts["untracked_files"] = len([l for l in lines if l.startswith("??")])

        ignore_files = []
        current = self.root
        while True:
            candidate = current / ".gitignore"
            if candidate.is_file():
                ignore_files.append(candidate)
            if current == git_root:
                break
            if git_root not in current.parents:
                break
            current = current.parent
        facts["has_gitignore"] = bool(ignore_files)
        patterns = []
        for gi in ignore_files:
            try:
                patterns.extend(l.strip() for l in gi.read_text(errors="ignore").splitlines()
                                if l.strip() and not l.startswith("#"))
            except OSError:
                pass
        facts["gitignore_pattern_count"] = len(patterns)

        # Which artifact directories found on disk are actually covered?
        uncovered, tracked_artifacts = [], []
        for a in self.artifact_dirs:
            covered = git_path_ignored(self.root, a["path"])
            if not covered:
                uncovered.append(a["path"])
            if any(t == a["path"] or t.startswith(a["path"] + "/") for t in tracked):
                tracked_artifacts.append(a["path"])
        facts["artifact_dirs_not_in_gitignore"] = uncovered[:self.top]
        facts["artifact_dirs_tracked_in_git"] = tracked_artifacts[:self.top]

        # Secrets are the highest-severity finding available, so resolve tracked status
        # precisely rather than inferring it.
        for s in self.secret_candidates:
            s["tracked_in_git"] = s["path"] in tracked
        facts["tracked_secret_candidates"] = [
            s["path"] for s in self.secret_candidates if s.get("tracked_in_git")
        ]
        return facts

    def largest_dirs(self):
        return sorted(
            ({"path": d["path"], "n_files": d["n_files"], "n_subdirs": d["n_subdirs"]}
             for d in self.dirs if d["path"] != "."),
            key=lambda d: -d["n_files"],
        )[:self.top]

    def single_file_dirs(self):
        return [{"path": d["path"], "file": d.get("only_file")}
                for d in self.dirs if "only_file" in d][:self.top]

    # -- assemble -----------------------------------------------------------------------

    def report(self):
        self.walk()
        git = self.git_facts()
        return {
            "scan": {
                "tool": "scan_structure.py",
                "version": "2.0",
                "target": str(self.root),
                "target_name": self.root.name,
                "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "max_depth": self.max_depth,
                "read_only": True,
            },
            "totals": {
                "directories": len(self.dirs),
                "files": self.file_count,
                "bytes": self.total_bytes,
                "size_human": human_size(self.total_bytes),
                "deepest_level": self.deepest,
                "hit_depth_limit": bool(self.pruned_directories),
            },
            "tree": {
                "directories": sorted(self.dirs, key=lambda item: item["path"]),
                "truncated": bool(self.pruned_directories),
            },
            "root": self.root_inventory(),
            "entry_points": self.entry_points(),
            "profile_signals": self.profile_signals(),
            "naming": self.naming(),
            "duplication": self.duplicates(),
            "nested_checkouts": self.nested_checkouts[:self.top],
            "project_layout_candidates": self.layout_candidates(),
            "configuration": self.config_landscape(),
            "secrets": {
                "high_confidence": [s for s in self.secret_candidates
                                    if s["confidence"] == "high"][:self.top],
                "low_confidence": [s for s in self.secret_candidates
                                   if s["confidence"] == "low"][:self.top],
                "count": len(self.secret_candidates),
                "note": "Filename-based detection only — a name match is a lead, not proof. "
                        "Open or confirm each one before reporting it. High-confidence hits "
                        "are credential-bearing by name; low-confidence hits are name hints "
                        "that often turn out to be code that *handles* a credential.",
            },
            "artifacts": {
                "directories": sorted(self.artifact_dirs,
                                      key=lambda a: -a["size_bytes"])[:self.top],
                "count": len(self.artifact_dirs),
                "total_bytes": sum(a["size_bytes"] for a in self.artifact_dirs),
                "total_human": human_size(sum(a["size_bytes"] for a in self.artifact_dirs)),
            },
            "lifecycle": {
                "archive_dirs": self.archive_dirs[:self.top],
                "scratch_dirs": self.scratch_dirs[:self.top],
                "audit_dirs": self.audit_dirs[:self.top],
                "empty_dirs": self.empty_dirs[:self.top],
                "empty_dir_count": len(self.empty_dirs),
                "zero_byte_files": self.zero_byte_files[:self.top],
                "zero_byte_count": len(self.zero_byte_files),
                "sentinel_files": self.sentinel_files[:self.top],
                "single_file_dirs": self.single_file_dirs(),
            },
            "freshness": self.mtime_analysis(),
            "git": git,
            "extensions": dict(self.ext_counter.most_common(30)),
            "largest_directories": self.largest_dirs(),
            "coverage_gaps": {
                "unreadable_paths": self.skipped_unreadable[:20],
                "depth_limited": bool(self.pruned_directories),
                "pruned_directories": sorted(self.pruned_directories)[:self.top],
                "opaque_artifact_dirs": sorted(a["path"] for a in self.artifact_dirs)[:self.top],
                "generated_reports_excluded": self.generated_reports_excluded,
                "note": "Anything listed here was not inspected. Report it as a coverage "
                        "gap rather than assuming it is clean.",
            },
        }


def main():
    ap = argparse.ArgumentParser(description="Read-only structural inventory of a repository.")
    ap.add_argument("target", help="Path to the repository or folder to scan")
    ap.add_argument("--max-depth", type=int, default=8, help="Directory depth limit (default 8)")
    ap.add_argument("--top", type=int, default=40, help="Max items per list (default 40)")
    ap.add_argument("--output", help="Write JSON here instead of stdout")
    args = ap.parse_args()

    target = Path(args.target).expanduser()
    if not target.exists():
        print(json.dumps({"error": f"target does not exist: {target}"}), file=sys.stderr)
        return 2
    if not target.is_dir():
        print(json.dumps({"error": f"target is not a directory: {target}"}), file=sys.stderr)
        return 2

    output = None
    if args.output:
        output = Path(args.output).expanduser().resolve()
        target_root = target.resolve()
        try:
            output.relative_to(target_root)
            print(json.dumps({"error": "output must be outside the target"}), file=sys.stderr)
            return 2
        except ValueError:
            pass
        if output.exists():
            print(json.dumps({"error": f"output already exists: {output}"}), file=sys.stderr)
            return 2

    report = Scanner(target, max_depth=args.max_depth, top=args.top).report()
    text = json.dumps(report, indent=2, sort_keys=False)

    if output:
        try:
            with output.open("x", encoding="utf-8") as handle:
                handle.write(text)
        except FileExistsError:
            print(json.dumps({"error": f"output already exists: {output}"}), file=sys.stderr)
            return 2
        print(f"Wrote {output} ({len(text)} bytes)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
