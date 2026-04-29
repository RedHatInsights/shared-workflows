# Shared GitHub Actions Workflows

This repository contains a collection of reusable GitHub Actions workflows and canonical PR templates shared across HCC (Hybrid Cloud Console) repositories in the [RedHatInsights](https://github.com/RedHatInsights) organization.

## Repository Contents

| Directory | Purpose |
|-----------|---------|
| `.github/workflows/` | Reusable GitHub Actions workflows |
| `.github/scripts/` | Supporting Python scripts for workflows |
| `pr-templates/` | Canonical PR templates for HCC repos ([details](pr-templates/README.md)) |
| `docs/` | Documentation and development guidelines |

### Available Workflows

| Workflow | Description | Docs |
|----------|-------------|------|
| `stale.yml` | Marks and closes stale issues/PRs | [docs/stale.md](docs/stale.md) |
| `sc-environment-impact-check.yml` | Assesses PR impact on SC Environment deployments | [SC_CHECK_README.md](.github/scripts/SC_CHECK_README.md) |
| `example.yml` | Minimal reusable workflow template | — |

### PR Templates

See [pr-templates/README.md](pr-templates/README.md) for which template to use and how to adopt them in your repository.

## Development

### 1. Basic Structure

Create a new file in the `.github/workflows/` directory with the following structure:

```yaml
name: Reusable Workflow Name

# The workflow_call trigger designates this as a reusable workflow
on:
  workflow_call:
    # Define inputs (parameters) that can be passed to the workflow
    inputs:
      input_name:
        description: 'Description of the input'
        required: false  # or true if the input is mandatory
        type: string     # Valid types: boolean, number, string
        default: 'default value'  # Optional default value
    
    # Define secrets that can be passed to the workflow
    secrets:
      secret_name:
        description: 'Description of the secret'
        required: false  # or true if the secret is mandatory

# Define the jobs in your workflow
jobs:
  job_name:
    name: Job Name
    runs-on: ubuntu-latest  # or any other runner
    steps:
      - name: Step Name
        run: echo "Hello from reusable workflow"
      
      # Access inputs using the inputs context
      - name: Use Input
        run: echo "Input value is ${{ inputs.input_name }}"
      
      # Access secrets using the secrets context
      - name: Use Secret
        run: |
          echo "Using secret (don't actually echo secrets in production workflows)"
          echo "Secret length: ${#ACTUAL_SECRET}"
        env:
          ACTUAL_SECRET: ${{ secrets.secret_name }}
```

## Usage

### Basic Usage

To use a reusable workflow in another repository, add a new workflow file with:

```yaml
name: My Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  call-reusable-workflow:
    uses: RedHatInsights/shared-workflows/.github/workflows/example.yml@master
```

## Passing Inputs and Secrets

### Passing Inputs

To pass inputs to a reusable workflow:

```yaml
jobs:
  call-reusable-workflow:
    uses: RedHatInsights/shared-workflows/.github/workflows/example.yml@master
    with:
      input_name: 'value'
      another_input: ${{ github.repository }}
```

### Passing Secrets

To pass secrets to a reusable workflow:

```yaml
jobs:
  call-reusable-workflow:
    uses: RedHatInsights/shared-workflows/.github/workflows/example.yml@master
    secrets:
      secret_name: ${{ secrets.YOUR_REPO_SECRET }}
      # To pass all secrets
      # inherit: true  # Requires GitHub Actions v2.3.0 or later
```

## Further Documentation

- [Workflow Development Guidelines](docs/workflow-guidelines.md) — conventions for creating reusable workflows
- [PR Template Guidelines](docs/pr-template-guidelines.md) — conventions for creating PR templates
- [AI Agent Guide](AGENTS.md) — onboarding guide for AI-assisted development
