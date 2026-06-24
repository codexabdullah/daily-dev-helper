"""Command-line interface entry points for Daily Dev Helper."""

from __future__ import annotations

import click

from dev_helper.core.git_tools import (
    GitCommandError,
    GitNotInstalledError,
    NotAGitRepositoryError,
    get_git_summary,
)


@click.group()
@click.version_option()
def main() -> None:
    """Daily Dev Helper: a CLI toolkit for everyday developer workflows."""


@main.group(name="git")
def git_group() -> None:
    """Utilities for working with local Git repositories."""


@git_group.command(name="summary")
def git_summary() -> None:
    """Display a quick, color-coded summary of the current repository."""
    try:
        summary = get_git_summary()
    except (GitNotInstalledError, NotAGitRepositoryError, GitCommandError) as exc:
        click.secho(f"✗ {exc}", fg="red", bold=True)
        raise SystemExit(1) from exc

    click.secho("Git Repository Summary", fg="white", bold=True, underline=True)
    click.echo()

    click.secho("Branch:         ", fg="white", nl=False)
    click.secho(summary.branch, fg="cyan", bold=True)

    click.secho("Status:         ", fg="white", nl=False)
    if summary.is_clean:
        click.secho("clean ✓", fg="green", bold=True)
    else:
        click.secho("modified/untracked files present ⚠", fg="yellow", bold=True)

    click.secho("Latest commit:  ", fg="white", nl=False)
    click.secho(f"{summary.latest_commit_hash} ", fg="magenta", bold=True, nl=False)
    click.secho(summary.latest_commit_subject, fg="white")


if __name__ == "__main__":
    main()
