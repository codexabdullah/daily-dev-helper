# 🚀 Daily Dev Helper

A production-grade, minimalist, and highly engineered CLI toolkit designed to eliminate daily developer friction and automate workflows.

---

## 🛠️ Features
* **Git Repository Summary:** Audits local repository states, extracts current branches, and tracks HEAD cleanliness using lightweight subprocess architecture.
* **Pre-commit Automation:** Strict industry coding standards with built-in hooks for formatting and syntax sanity via Ruff.

## 🚀 Installation & Usage

To use this tool locally on your machine, clone the repository and install it in editable mode:

```bash
# Clone the repository
git clone [https://github.com/codexabdullah/daily-dev-helper.git](https://github.com/codexabdullah/daily-dev-helper.git)

# Navigate into the project directory
cd daily-dev-helper

# Set up virtual environment (Recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\Activate.ps1

# Install in development mode
pip install -e .
