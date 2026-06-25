# Daily Dev Helper 🚀

A minimal, engineered CLI toolkit for software engineers to automate standup reporting, diagnostics, and workspace security audits. Built with Python and Click.

## 🛠️ Installation & Setup

```powershell
# Clone the repository
git clone https://github.com/your-username/daily-dev-helper.git

# Navigate into the project directory
cd daily-dev-helper

# Create a Python virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install the package in editable mode
pip install --editable .
```

## 🚀 Core CLI Commands

### 1. Diagnostics
Verifies that the CLI framework and entry points are operational.

```bash
dev-helper status
```

### 2. Git Standup Report
Compiles local commit history headers from the last N days.

```bash
dev-helper git standup --days 1
```

### 3. Security Workspace Scanner
Audits local files for exposed keys/tokens while automatically pruning `.venv` and `.git`.

```bash
dev-helper git scan
```

## 🧪 Quick Verification Sandbox (Testing Protocol)

Run this unified sequence to safely verify the security scanner engine against high-entropy mock artifacts:

```powershell
Set-Content -Path "test_secrets.py" -Value "db_password = 'super_secret_password_123'`ngithub_token = 'ghp_1234567890abcdef1234567890abcdef1234'"
dev-helper git scan
Remove-Item -Path "test_secrets.py" -Force
```

## 🛡️ Code Quality Standards

Enforced automatically via pre-commit hooks featuring Ruff Linter and Ruff Formatter.
