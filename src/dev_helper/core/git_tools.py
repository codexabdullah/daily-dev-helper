"""Utilities for querying local Git repository information.

This module provides safe, read-only access to common Git metadata
(current branch, working tree status, and latest commit) using the
standard library's ``subprocess`` module. It deliberately avoids any
third-party Git bindings to keep the dependency footprint minimal.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


class GitNotInstalledError(RuntimeError):
    """Raised when the ``git`` executable cannot be found on PATH."""


class NotAGitRepositoryError(RuntimeError):
    """Raised when the current directory is not inside a Git repository."""


class GitCommandError(RuntimeError):
    """Raised when a git subprocess call fails for an unexpected reason."""


@dataclass(frozen=True, slots=True)
class GitSummary:
    """An immutable snapshot of the local repository's current state."""

    branch: str
    is_clean: bool
    latest_commit_hash: str
    latest_commit_subject: str


def _ensure_git_available() -> None:
    """Verify that the ``git`` executable is available on PATH.

    Raises:
        GitNotInstalledError: If ``git`` cannot be located.
    """
    if shutil.which("git") is None:
        raise GitNotInstalledError(
            "Git executable not found. Please install Git and ensure it "
            "is available on your PATH."
        )


def _run_git_command(*args: str) -> str:
    """Run a git command and return its stripped stdout output.

    Args:
        *args: Arguments passed to ``git`` (excluding the binary itself).

    Returns:
        The command's standard output, stripped of surrounding whitespace.

    Raises:
        GitNotInstalledError: If ``git`` is not installed or not executable.
        NotAGitRepositoryError: If the current directory is not a git repo.
        GitCommandError: For any other non-zero git exit status.
    """
    _ensure_git_available()

    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise GitNotInstalledError(f"Failed to execute git: {exc}") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "not a git repository" in stderr.lower():
            raise NotAGitRepositoryError(
                "The current directory is not inside a Git repository."
            )
        raise GitCommandError(
            f"Git command failed (exit code {result.returncode}): "
            f"{stderr or 'unknown error'}"
        )

    return result.stdout.strip()


def get_current_branch() -> str:
    """Return the name of the currently checked-out branch.

    Returns:
        The branch name, or ``detached@<short_hash>`` if HEAD is detached.
    """
    branch = _run_git_command("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "HEAD":
        short_hash = _run_git_command("rev-parse", "--short", "HEAD")
        return f"detached@{short_hash}"
    return branch


def is_working_directory_clean() -> bool:
    """Check whether the working directory has no uncommitted changes.

    Returns:
        ``True`` if there are no staged, modified, or untracked files.
    """
    status_output = _run_git_command("status", "--porcelain")
    return status_output == ""


def get_latest_commit() -> tuple[str, str]:
    """Return the short hash and subject line of the latest commit.

    Returns:
        A ``(short_hash, subject_line)`` tuple.
    """
    # 0x1f (unit separator) avoids collisions with characters in commit subjects.
    output = _run_git_command("log", "-1", "--pretty=format:%h\x1f%s")
    short_hash, _, subject = output.partition("\x1f")
    return short_hash, subject


def get_git_summary() -> GitSummary:
    """Gather a complete summary of the current repository state.

    Returns:
        A populated :class:`GitSummary` instance.

    Raises:
        GitNotInstalledError: If git is not installed.
        NotAGitRepositoryError: If not inside a git repository.
        GitCommandError: For other unexpected git failures.
    """
    branch = get_current_branch()
    is_clean = is_working_directory_clean()
    commit_hash, commit_subject = get_latest_commit()

    return GitSummary(
        branch=branch,
        is_clean=is_clean,
        latest_commit_hash=commit_hash,
        latest_commit_subject=commit_subject,
    )
