# Shared GitHub Actions Workflows

This repository contains a collection of reusable GitHub Actions workflows that can be shared across multiple repositories within our organization.

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
