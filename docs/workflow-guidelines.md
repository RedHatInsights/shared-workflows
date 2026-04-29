# Workflow Development Guidelines

Rules and conventions for creating and maintaining reusable GitHub Actions workflows in this repository.

## Workflow Structure

### File Location

- All reusable workflows live in `.github/workflows/`
- Supporting scripts live in `.github/scripts/`
- Configuration files live in `.github/` (e.g., `sc-environment-impact-config.yml`)
- Documentation for workflows goes in `docs/` with a matching name (e.g., `docs/stale.md` for `stale.yml`)

### Reusable Workflow Pattern

Every workflow must use the `workflow_call` trigger to be callable from other repositories:

```yaml
on:
  workflow_call:
    inputs:
      input_name:
        description: 'Clear description of the input'
        required: false
        type: string
        default: 'sensible default'
    secrets:
      secret_name:
        description: 'Clear description of the secret'
        required: false
```

### Caller Reference Format

Consumers call workflows with:
```yaml
uses: RedHatInsights/shared-workflows/.github/workflows/<name>.yml@master
```

Always reference `@master` (the default branch), not specific commits or tags.

## Input and Secret Conventions

- Provide sensible defaults for all optional inputs
- Use `required: true` sparingly — prefer defaults to reduce caller boilerplate
- Use `type: string`, `type: boolean`, or `type: number` — no other types are supported
- Document every input and secret with a `description` field
- Secret names should use `SCREAMING_SNAKE_CASE`
- Input names should use `kebab-case`

## Permissions

Reusable workflows do NOT inherit permissions from the `permissions:` block in the workflow file. Callers must set their own permissions. Document required permissions in the workflow's companion doc in `docs/`:

```yaml
# Caller workflows must set these permissions themselves.
# This block applies only if the workflow is run directly.
permissions:
  pull-requests: write
  contents: read
```

## Supporting Scripts

### Python Scripts

- Target Python 3.11+ (set in `actions/setup-python`)
- Keep dependencies minimal — install only what's needed (e.g., `pip install PyYAML`)
- Use `#!/usr/bin/env python3` shebang
- Include a module docstring describing the script's purpose
- Use `argparse` for CLI argument parsing
- Write output to well-known paths (e.g., `/tmp/`) for consumption by subsequent workflow steps
- Exit with `sys.exit(0)` on success, `sys.exit(1)` on failure

### Shell Scripts

- Use `#!/bin/bash` or `#!/usr/bin/env bash`
- Prefer inline `run:` blocks in the workflow YAML for simple operations
- Extract to `.github/scripts/` only when logic is complex enough to warrant a separate file

## Checkout and Context

When a workflow needs files from this repo (scripts, configs), use a second checkout step:

```yaml
- name: Checkout shared-workflows repo
  uses: actions/checkout@v4
  with:
    repository: ${{ github.repository_owner }}/shared-workflows
    path: _tools
    ref: master
```

Use a distinctive path prefix (e.g., `_tools`, `_sc_check_tools`) to avoid collisions with the caller's checkout.

## Documentation

- Every non-trivial workflow must have a companion doc in `docs/<workflow-name>.md`
- Include: purpose, usage example (YAML snippet), required permissions, input/secret reference, and how it works internally
- The `docs/` companion doc is the primary reference. `README.md` provides only a brief overview with a link

## Testing

- Test detection patterns and scripts locally before committing
- For Python scripts: document local test commands in the companion doc
- For workflows: provide a minimal caller example in `docs/` so consumers can test adoption

## Versioning

- This repo uses a single `master` branch — no release tags
- Breaking changes to existing workflows should be documented in the PR description and communicated to consuming teams
- Prefer additive changes (new inputs with defaults) over breaking interface changes
