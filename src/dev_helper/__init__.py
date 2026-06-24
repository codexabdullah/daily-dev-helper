"""Daily Dev Helper: a CLI toolkit of everyday utilities for developers."""

# Single source of truth for the package version. cli.py imports this rather
# than hardcoding a second copy. Keep this in sync with the `version` field
# in pyproject.toml until the project switches to setuptools-scm or
# importlib.metadata for automatic version resolution.
__version__ = "0.1.0"
