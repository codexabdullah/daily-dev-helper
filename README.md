# Daily Dev Helper 🚀

A modular, lightweight CLI toolkit engineered for software engineers to streamline everyday development workflows, automate standup reporting, and audit local workspace security. Built natively using the Python Standard Library and the Click framework.

---

## 🛠️ Installation & Setup

1. Clone the repository and navigate to the project root:
   ```powershell
   git clone <your-repository-url>
   cd daily-dev-helper
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install --editable .
🚀 Core Commands & Testing Protocols
1. Diagnostics (status)
Verifies that the CLI framework and entry points are resolving correctly.

Command: dev-helper status

Expected Output: Daily Dev Helper is active!

2. Standup Report (git standup)
Generates structured daily standup status reports by compiling local Git commit history headers within a configurable window.

Command: dev-helper git standup --days 1

Expected Output: Summarized list of commit activity headers parsed from HEAD.

3. Workspace Security Audit (git scan)
Heuristic regex engine that scans local source code for exposed hardcoded tokens, passwords, or keys while automatically pruning .venv, .git, and dependency caches.

Command: dev-helper git scan

Target Vectors: Generic assignments (db_password = '...'), GitHub PATs (ghp_...), and AWS IDs (AKIA...).

🧪 Quick Verification Sandbox (Testing Sequence)
Execute this unified multi-step powershell block in your terminal to safely verify the credential scanner's accuracy against mock sandbox data:

PowerShell
# Step 1: Plant mock secrets in a temporary verification file
Set-Content -Path "test_secrets.py" -Value "db_password = 'super_secret_password_123'`ngithub_token = 'ghp_1234567890abcdef1234567890abcdef1234'"

# Step 2: Trigger the validation audit
dev-helper git scan

# Step 3: Purge the temporary mock artifact from your workspace
Remove-Item -Path "test_secrets.py" -Force
🛡️ Code Quality Standards
This repository enforces absolute architectural sanity via automated pre-commit hooks featuring Ruff Linter (ruff-check) for syntax optimization and Ruff Formatter (ruff format) for production styling consistency.


---

### Step 2: GitHub Par Push Maaro

Isko save kar ke close karo aur ab dasti terminal par ye commands chalao taake yeh clean single-block layout GitHub par chala jaye:

```powershell
git add README.md
git commit -m "docs: unify README structure into a single concise framework"
git push origin main
