"""
Command-line interface for Daily Dev Helper.

This module defines `main`, the Click group registered in pyproject.toml
under [project.scripts] as the `dev-helper` command. Every feature of the
toolkit is attached to this group as a subcommand (e.g., `dev-helper status`,
`dev-helper git standup`, `dev-helper git scan`, and later
`dev-helper todo ...`, etc.).
"""

import click

from dev_helper import __version__
from dev_helper.core.git_tools import get_recent_commits, scan_local_secrets


@click.group()
@click.version_option(version=__version__, prog_name="dev-helper")
def main() -> None:
    """Daily Dev Helper: a CLI toolkit of everyday utilities for developers.

    Run `dev-helper COMMAND --help` for details on a specific command.
    """
    # No group-level logic yet. This function body stays empty on purpose —
    # Click uses its docstring as the top-level --help text, and this is the
    # natural place to later attach shared state (e.g., a config object via
    # `ctx.obj`) that every subcommand below can read.


@main.command()
def status() -> None:
    """Check that the CLI is installed and wired up correctly."""
    # Placeholder command. Confirms the entry point resolves end-to-end:
    # `dev-helper` -> `dev_helper.cli:main` -> this subcommand.
    click.echo("Daily Dev Helper is active!")


# ---------------------------------------------------------------------------
# `dev-helper git ...` — subcommands related to Git history and reporting.
# ---------------------------------------------------------------------------
@main.group(name="git")
def git_group() -> None:
    """Git-related utilities and reports."""
    # The group carries no logic of its own; it exists purely to namespace
    # the commands below under `dev-helper git <subcommand>`. Note the
    # function is named `git_group` (not `git`) so it never shadows the
    # `git` package (e.g., GitPython) if `core.git_tools` ends up using it.


@git_group.command()
@click.option(
    "--days",
    type=int,
    default=1,
    show_default=True,
    help="Number of past days of commit history to include in the report.",
)
def standup(days: int) -> None:
    """Generate a Daily Standup Report from recent commits.

    Summarizes commit activity from the last DAYS days, so you can quickly
    answer "what did I work on?" at the start of a standup meeting.
    """
    # Delegate entirely to the core layer. The CLI stays a thin presentation
    # wrapper: it knows how to ask for data and how to render it, not how
    # Git itself works. That logic belongs in dev_helper.core.git_tools.
    commits = get_recent_commits(days)

    if not commits:
        click.echo(f"No commits found in the last {days} days.")
        return

    day_label = "day" if days == 1 else "days"
    commit_label = "commit" if len(commits) == 1 else "commits"

    # Header. click.style() applies ANSI bold/underline and degrades
    # gracefully to plain text when stdout isn't a terminal (e.g., when
    # output is piped to a file or another program).
    click.echo(click.style("Daily Standup Report", bold=True, underline=True))
    click.echo(f"{len(commits)} {commit_label} in the last {days} {day_label}\n")

    # Body: one bullet per commit. Each `commit` is assumed to be a plain
    # string (the commit's summary line) per the current
    # `get_recent_commits` contract.
    for commit in commits:
        click.echo(f"  • {commit}")


@git_group.command()
def scan() -> None:
    """Scan the current directory for hardcoded secrets and credentials.

    Delegates entirely to `dev_helper.core.git_tools.scan_local_secrets`,
    which walks the working directory tree and checks each file against
    a set of known secret patterns (generic API keys/tokens/passwords,
    GitHub Personal Access Tokens, and AWS Access Key IDs). This command's
    only job is to render the result; it contains no scanning logic itself.
    """
    findings = scan_local_secrets()

    if not findings:
        click.echo(
            click.style(
                "No hardcoded secrets or credentials found. Repository is safe.",
                fg="green",
                bold=True,
            )
        )
        return

    # Sort for stable, readable output. os.walk's traversal order depends
    # on the filesystem and is not guaranteed, but grouping findings by
    # file path (then line number) is always what a developer wants to see.
    findings = sorted(findings)
    finding_label = "secret" if len(findings) == 1 else "secrets"

    # High-visibility warning header: bold red text is the universal
    # "stop and look at this" signal in a terminal. click.style() degrades
    # to plain text automatically when stdout isn't a terminal (e.g., when
    # output is piped to a file or captured by another program).
    click.echo(
        click.style(
            f"⚠ WARNING: {len(findings)} potential {finding_label} detected!",
            fg="red",
            bold=True,
        )
    )
    click.echo()

    for file_path, line_number, secret_type in findings:
        location = click.style(f"{file_path}:{line_number}", fg="yellow")
        label = click.style(secret_type, fg="red", bold=True)
        click.echo(f"  {location} — {label}")

    click.echo()
    click.echo(
        "Review the lines above and remove or rotate any real credentials "
        "before committing."
    )


# Allows running this file directly during development, e.g.
# `python -m dev_helper.cli status`, without needing the installed
# entry point. Has no effect when invoked via the `dev-helper` command.
if __name__ == "__main__":
    main()
