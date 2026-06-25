"""
Core engine for Daily Dev Helper.

This module holds the toolkit's "core logic" -- pure functions that accept
primitive inputs and return plain data structures, with no awareness of
Click, terminal colors, or how their output will eventually be displayed.
Presentation is handled entirely by `dev_helper.cli`; this module focuses
only on producing correct data.
"""

import os
import re
import subprocess


def get_recent_commits(days: int) -> list[str]:
    """Return commit summary lines from the local Git history.

    Args:
        days: Number of past days of history to include.

    Returns:
        A list of commit summary strings (one per commit), most recent
        first. Returns an empty list if the current directory is not a
        Git repository, Git is not installed, or no commits fall within
        the requested window.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"--since={days}.days", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        # Git itself is not installed, or not available on PATH.
        return []

    if result.returncode != 0:
        # Most commonly: the current directory is not inside a Git
        # repository. Fail soft rather than raising, since the CLI layer
        # treats "no commits" and "not a repo" identically.
        return []

    # `git log` prints an empty string (not an error) when there are no
    # matching commits, so guard against turning that into one blank entry.
    output = result.stdout.strip()
    if not output:
        return []

    return output.split("\n")


# ---------------------------------------------------------------------------
# Local secret / credential scanner
# ---------------------------------------------------------------------------

# Directories that are never worth scanning: version control metadata,
# virtual environments, bytecode/tool caches, and dependency folders. None
# of these contain a developer's own source code, and the largest ones
# (notably node_modules and .venv) would otherwise dominate scan time.
_SKIPPED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    "node_modules",
    "build",
    "dist",
}

# Pattern 1 -- a generic "name = value" / "name: value" assignment where the
# name strongly suggests a credential (key, secret, token, or password) and
# the value is a quoted string of meaningful length. There is deliberately
# no word boundary before the keyword: real-world variable names commonly
# *end* with it (db_password, USER_TOKEN, aws_secret), and a leading \b
# would silently miss every one of those. The `\s*[:=]` requirement right
# after the keyword still prevents matches inside unrelated words (e.g.
# "passwordless_flag" does not match, since "less_flag" follows "password"
# instead of an assignment operator). This pattern favors recall over
# precision on purpose -- a credential scanner should flag too much rather
# than silently miss a real secret.
_GENERIC_SECRET_PATTERN = re.compile(
    r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*"
    r"['\"]([^'\"]{8,})['\"]"
)

# Pattern 2 -- classic GitHub Personal Access Tokens: "ghp_" followed by
# 36 alphanumeric characters.
_GITHUB_PAT_PATTERN = re.compile(r"\bghp_[A-Za-z0-9]{36}\b")

# Pattern 3 -- AWS Access Key IDs: "AKIA" followed by 16 uppercase
# alphanumeric characters.
_AWS_ACCESS_KEY_PATTERN = re.compile(r"\bAKIA[0-9A-Z]{16}\b")

# Maps each compiled pattern to a short, human-readable label for the kind
# of secret it detects. Centralizing this mapping is what lets
# `scan_local_secrets` stay generic -- adding a new secret type later means
# adding one entry here, not touching the scanning logic itself.
_SECRET_PATTERNS: dict[re.Pattern[str], str] = {
    _GITHUB_PAT_PATTERN: "GitHub Personal Access Token",
    _AWS_ACCESS_KEY_PATTERN: "AWS Access Key ID",
    _GENERIC_SECRET_PATTERN: "Generic API Key/Secret/Token/Password",
}


def scan_local_secrets() -> list[tuple[str, int, str]]:
    """Scan the current working directory tree for likely hardcoded secrets.

    Walks every file under the current working directory using
    `os.walk`, skipping directories that are never useful to scan
    (version control metadata, virtual environments, caches, dependency
    folders), and checks each line of each remaining file against a set
    of known secret patterns: generic key/secret/token/password
    assignments, GitHub Personal Access Tokens, and AWS Access Key IDs.

    This is a lightweight, dependency-free heuristic scanner -- it is
    intended to catch obvious, accidentally committed credentials, not
    to replace a dedicated, entropy-based secret-scanning service.

    Returns:
        A list of (file_path, line_number, matched_secret_type) tuples,
        one entry per match. `line_number` is 1-indexed. The list is
        empty if no matches are found.
    """
    findings: list[tuple[str, int, str]] = []

    for root, dirs, files in os.walk("."):
        # Mutating `dirs` in place tells os.walk not to descend into these
        # directories at all, which is what actually saves time on large
        # repositories -- filtering the results afterward would not.
        dirs[:] = [directory for directory in dirs if directory not in _SKIPPED_DIRS]

        for filename in files:
            file_path = os.path.join(root, filename)
            findings.extend(_scan_file_for_secrets(file_path))

    return findings


def _scan_file_for_secrets(file_path: str) -> list[tuple[str, int, str]]:
    """Scan a single file, line by line, for known secret patterns.

    Kept separate from `scan_local_secrets` so that each file's I/O and
    decoding concerns (binary content, unreadable files, encoding
    errors) are handled in one place, without complicating the
    directory-walking logic above.

    Args:
        file_path: Path to the file to scan, as yielded by os.walk.

    Returns:
        A list of (file_path, line_number, matched_secret_type) tuples
        for this file only.
    """
    matches: list[tuple[str, int, str]] = []

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as handle:
            for line_number, line in enumerate(handle, start=1):
                for pattern, secret_type in _SECRET_PATTERNS.items():
                    if pattern.search(line):
                        matches.append((file_path, line_number, secret_type))
    except (OSError, UnicodeDecodeError):
        # Skip files that can't be opened or decoded (binary files,
        # permission errors, broken symlinks, etc.) rather than letting
        # one problematic file abort the entire scan.
        pass

    return matches
