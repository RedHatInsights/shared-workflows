@AGENTS.md

# Claude Code Configuration

## Build and Test Commands

This repo has no build step or test suite. To verify Python scripts:

```bash
# Install dependencies
pip install PyYAML

# Verify SC impact checker runs
python .github/scripts/sc_environment_impact_check.py --help

# Test impact analysis locally (requires a git repo with commits)
python .github/scripts/sc_environment_impact_check.py \
  --base-ref HEAD~1 --head-ref HEAD --output-format markdown
```

## Workflow File Restriction

Do NOT modify files under `.github/workflows/`. The bot PAT lacks the `workflow` scope and pushes will fail. If a task requires workflow changes, note this in a Jira comment and skip the modification.

## Commit Convention

Use conventional commits: `type(scope): description`

Scopes: `workflows`, `scripts`, `pr-templates`, `docs`

Examples:
- `feat(workflows): add reusable lint workflow`
- `fix(scripts): handle empty diff in impact checker`
- `docs(pr-templates): add backend template`
