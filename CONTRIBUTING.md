# Contributing to Sunona Voice AI

Thank you for your interest in contributing to Sunona! 🎉

We welcome contributions from the community, whether it's bug reports, feature requests, documentation improvements, or code contributions.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Master Branch Protection](#-master-branch-protection--enforcement)
- [Handling Rule Violations (GH013)](#%EF%B8%8F-handling-repository-rule-violations-gh013)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#-reporting-bugs)
  - [Suggesting Features](#-suggesting-features)
  - [Contributing Code](#-contributing-code)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and considerate in communications
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🛡️ Master Branch Protection & Enforcement

The `master` branch is protected with industry-level rules. All contributors must follow these guidelines when contributing code.

### 🔐 Branch Access Restrictions
- **No direct pushes** → All changes must go through Pull Requests (PRs).
- **No branch deletions** → `master` cannot be deleted.
- **No force pushes** → History cannot be overwritten.
- **No unauthorized updates/creations** → Only maintainers or CI/CD bots can bypass.

### 📜 Commit & Merge Requirements
- **Linear history required** → No merge commits; use rebase or squash.
- **Merge queue enforced** → PRs are merged in order via queue.
- **Concurrency**: 5 PRs can run checks at once.
- **Group size**: 1–5 PRs per batch.
- **Wait time**: 5 minutes before merging if batching.
- **All PRs must pass checks** before merging.
- **Signed commits required** → All commits must be GPG/S/MIME signed.
- **Status checks required** → PRs must pass:
  - ✅ Build
  - ✅ Unit tests
  - ✅ Linting
  - ✅ Integration tests

### 🛡️ Security & Code Quality
- **Code scanning required** → Tools like CodeQL must report clean results.
- **Code quality checks required** → PRs blocked if issues are High or Critical.
- **Copilot code review enabled** → AI-assisted review runs automatically.
- **Static analysis tools integrated** → ESLint, PyLint, SonarQube (if configured).

### 🚀 Deployment Rules
- **Require deployments to succeed** → PRs must deploy successfully before merging.
- **Environments**:
  - `staging` → Pre-production testing
  - `production` → Live deployment
- **CI/CD bots handle deployments**; contributors cannot bypass.

### 🏢 Enterprise Restrictions (if applicable)
- **Commit metadata restricted** → Must use valid email domains and proper commit messages.
- **Branch names restricted** → Unsafe or ambiguous names are blocked.

### 👥 Bypass List
- Only trusted maintainers and CI/CD bots (e.g., `github-actions[bot]`) have bypass rights.
- General contributors do not have bypass permissions.

### ✅ Contributor Workflow
1. **Fork the repo** → Work on your own branch.
2. **Create a feature branch** → Example: `feature/voice-agent`.
3. **Commit with signatures** → Ensure commits are signed.
4. **Push branch to your fork**.
5. **Open a Pull Request** → Target `master`.
6. **Pass all checks** → Build, tests, lint, code scanning, deployment.
7. **Wait for merge queue** → Your PR will merge automatically once approved.

---

## 🛠️ Handling Repository Rule Violations (GH013)

If your push is declined with the error `GH013: Repository rule violations found`, it means you are attempting a direct push to a protected branch (like `master`).

### 🔍 How to Fix

1. **Review Branch Protection Rules**:
   Visit the [Repository Rules Page](https://github.com/Sunona-AI-labs/sunona/rules?ref=refs/heads/master) to see common restrictions (pull requests, signed commits, status checks).

2. **Adapt Your Workflow**:
   If direct pushes are not allowed, change your workflow (or GitHub Actions) to open a pull request instead.

   **Example (GitHub Actions):**
   ```yaml
   - name: Commit changes
     run: |
       git config user.name "github-actions[bot]"
       git config user.email "github-actions[bot]@users.noreply.github.com"
       git checkout -b update-branch
       git add .
       git commit -m "update changes [skip ci]"
       git push origin update-branch

   - name: Create Pull Request
     uses: peter-evans/create-pull-request@v6
     with:
       token: ${{ secrets.GITHUB_TOKEN }}
       branch: update-branch
       title: "Automated Update"
       base: master
   ```

3. **Ensure Compliance**:
   Ensure all commits are **GPG/S/MIME signed** and pass all required status checks before attempting to merge.

---

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/sunona.git
   cd sunona
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## How to Contribute

### 🐛 Reporting Bugs

Found a bug? Please help us fix it by creating a detailed bug report.

**Before submitting:**
- Check [existing issues](https://github.com/sap1119/sunona/issues) to avoid duplicates
- Make sure you're using the latest version

**To report a bug:**

1. Go to [Issues](https://github.com/sap1119/sunona/issues/new)
2. Click **"New Issue"**
3. Use this template:

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Windows 11, Ubuntu 22.04, macOS 14]
- Python version: [e.g., 3.11.5]
- Sunona version: [e.g., 0.1.0]

## Error Logs
```
Paste any error messages or logs here
```

## Additional Context
Any other relevant information.
```

---

### ✨ Suggesting Features

Have an idea for a new feature? We'd love to hear it!

**To suggest a feature:**

1. Go to [Issues](https://github.com/sap1119/sunona/issues/new)
2. Add the label `enhancement` or `feature-request`
3. Use this template:

```markdown
## Feature Description
A clear description of the feature you'd like.

## Use Case
Why do you need this feature? What problem does it solve?

## Proposed Solution
How do you envision this working?

## Alternatives Considered
Any alternative solutions you've thought about.

## Additional Context
Mockups, examples, or references.
```

---

### 💻 Contributing Code

We welcome code contributions! Here's how to get started:

#### Good First Issues

Looking for something to work on? Check out issues labeled:
- [`good first issue`](https://github.com/sap1119/sunona/labels/good%20first%20issue) - Great for newcomers
- [`help wanted`](https://github.com/sap1119/sunona/labels/help%20wanted) - We need your help!
- [`documentation`](https://github.com/sap1119/sunona/labels/documentation) - Improve our docs

#### Areas We Need Help With

| Area | Description |
|------|-------------|
| **New Providers** | Add support for new STT/TTS/LLM/Telephony providers |
| **Documentation** | Improve README, add tutorials, API docs |
| **Testing** | Add unit tests, integration tests |
| **Bug Fixes** | Fix reported issues |
| **Performance** | Optimize latency, reduce resource usage |
| **Examples** | Create new example scripts and use cases |

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- [Optional] Docker for local testing

### Setup Steps

```powershell
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/sunona.git
cd sunona

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install -e ".[dev]"

# 5. Copy environment template
cp .env.example .env
# Edit .env with your API keys (for testing)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sunona

# Run specific test file
pytest tests/test_transcriber.py
```

### Code Formatting

```bash
# Format code with Black
black sunona/

# Lint with Ruff
ruff check sunona/

# Type check (optional)
mypy sunona/
```

---

## Pull Request Process

### Before Submitting

1. ✅ Your code follows our [style guidelines](#style-guidelines)
2. ✅ You've added/updated tests for your changes
3. ✅ All tests pass (`pytest`)
4. ✅ You've updated documentation if needed
5. ✅ You've added an entry to `CHANGELOG.md` (under "Unreleased")

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template:**

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (describe)

## Related Issue
Fixes #123

## Testing
How did you test these changes?

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

4. **Wait for review** - Maintainers will review your PR and may request changes

5. **Address feedback** - Make requested changes and push updates

6. **Merge!** 🎉 - Once approved, your PR will be merged

---

## Style Guidelines

### Python Code Style

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters max
- **Formatter**: Black (enforced)
- **Linter**: Ruff
- **Type hints**: Encouraged for public APIs

### Code Examples

```python
# ✅ Good
async def process_audio(
    audio_data: bytes,
    sample_rate: int = 16000,
    language: str = "en-US",
) -> TranscriptionResult:
    """Process audio and return transcription.
    
    Args:
        audio_data: Raw audio bytes (PCM 16-bit)
        sample_rate: Audio sample rate in Hz
        language: Language code for transcription
        
    Returns:
        TranscriptionResult with text and metadata
    """
    # Implementation here
    pass

# ❌ Bad
async def proc_aud(d, sr=16000, l="en-US"):
    pass
```

### Commit Messages

Use clear, descriptive commit messages:

```
# ✅ Good
feat: add Azure Speech-to-Text provider
fix: resolve memory leak in audio buffer
docs: add Twilio quickstart guide
refactor: simplify transcriber factory

# ❌ Bad
fixed stuff
wip
update
```

**Format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

---

## Community

### Get Help

- 💬 **Discussions**: [GitHub Discussions](https://github.com/sap1119/sunona/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/sap1119/sunona/issues)
- 📧 **Email**: sathyaedu1119@gmail.com

### Stay Updated

- ⭐ **Star the repo** to show support
- 👁️ **Watch** for updates and releases
- 🐦 **Follow** for announcements

---

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Our contributors page

---

## License

By contributing to Sunona, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to Sunona! 🙏

Every contribution, no matter how small, helps make voice AI more accessible to everyone.
