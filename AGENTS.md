# Agent Guide

Onboarding guide for AI agents working in the `shared-workflows` repository.

## What This Repo Is

A collection of **reusable GitHub Actions workflows**, supporting scripts, and **PR templates** shared across HCC (Hybrid Cloud Console) frontend and backend repositories within the RedHatInsights organization.

This is NOT an application — it produces no runtime artifacts. Its outputs are:
- YAML workflow files consumed via `uses: RedHatInsights/shared-workflows/.github/workflows/<name>.yml@master`
- PR template files copied into consuming repos as `.github/PULL_REQUEST_TEMPLATE.md`

## Repository Structure

```
.github/
  workflows/          # Reusable GitHub Actions workflows
    example.yml       # Basic workflow template
    stale.yml         # Stale issue/PR handler
    sc-environment-impact-check.yml  # SC Environment impact assessment
  scripts/            # Supporting Python/shell scripts for workflows
    sc_environment_impact_check.py   # Impact analysis engine
    send_slack_notification.py       # Slack notification helper
  sc-environment-impact-config.yml   # Default config for SC impact checker
docs/                 # Documentation and guidelines
  stale.md            # Stale workflow usage docs
  workflow-guidelines.md   # How to develop workflows
  pr-template-guidelines.md  # How to develop PR templates
pr-templates/         # Canonical PR templates for HCC repos
  README.md           # Template selection guide
  frontend.md         # Frontend PR template
  backend.md          # Backend PR template
  infra.md            # Infrastructure PR template
```

## Domain-Specific Guidelines

Detailed conventions for each domain:

| Guideline | When to consult |
|-----------|-----------------|
| [Workflow Development](docs/workflow-guidelines.md) | Creating or modifying reusable GitHub Actions workflows |
| [PR Templates](docs/pr-template-guidelines.md) | Creating or modifying pull request templates |

## Key Conventions

### Default Branch

The default branch is `master`. Consumers reference workflows via `@master`.

### File Naming

- Workflow files: `kebab-case.yml` in `.github/workflows/`
- Python scripts: `snake_case.py` in `.github/scripts/`
- PR templates: `lowercase.md` in `pr-templates/`
- Documentation: `kebab-case.md` in `docs/`

### Workflow Inputs

- Input names use `kebab-case`
- Secret names use `SCREAMING_SNAKE_CASE`
- Always provide sensible defaults for optional inputs
- Every input and secret must have a `description` field

### No GitHub Workflows Modifications by Bots

Bot accounts (including AI agents) must NOT modify files under `.github/workflows/` — the PAT used by bots typically lacks the `workflow` scope, and pushes will be rejected. If a ticket requires workflow changes, note this limitation in a Jira comment and skip the workflow modification.

### Documentation Pairing

Every non-trivial workflow has a companion doc in `docs/`. When adding or modifying a workflow, update its companion doc. When the companion doc doesn't exist yet, create one.

## Common Pitfalls

- **Permissions**: Reusable workflows do NOT inherit the `permissions:` block from the workflow file. Callers must set their own permissions. Always document required permissions in the companion doc.
- **Checkout context**: When a workflow needs files from this repo (scripts, configs), use a separate checkout step with a distinctive `path:` to avoid overwriting the caller's checkout.
- **Self-detection**: The SC impact checker skips files under `.github/` to avoid flagging its own config changes. Keep this pattern when adding new detection workflows.
- **Python dependencies**: Install only what's needed. The scripts currently require only `PyYAML`. Adding new dependencies increases setup time for all consumers.

## Testing

- No automated test suite exists for the workflows themselves
- Python scripts can be tested locally: `pip install PyYAML && python .github/scripts/sc_environment_impact_check.py --help`
- Test workflow changes by creating a PR in this repo and verifying the workflow runs correctly
- For detection pattern changes, use the local test approach documented in `.github/scripts/SC_CHECK_README.md`
