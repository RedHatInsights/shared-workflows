# Stale

Marks issues and PRs stale after a period of inactivity and closes them after a
further grace period.

## Usage

```yml
name: Handle stale issues and PRs

on:
  schedule:
    - cron: "30 1 * * *"
  workflow_dispatch:

permissions:
  issues: write
  pull-requests: write

jobs:
  stale:
    uses: RedHatInsights/shared-workflows/.github/workflows/stale.yml@<commit-sha>
```

## Pinning

Reference this workflow by full commit SHA, not `@master`, so a change to
`shared-workflows` cannot alter behaviour in your repository without a PR. The
`actions/stale` step inside this workflow is pinned to a commit SHA for the same
reason, and Renovate opens PRs to keep that pin current.

## Permissions

Reusable workflows do not inherit the caller's `permissions:` block, so the
calling workflow must grant them. The stale action needs `issues: write` and
`pull-requests: write`.

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `days-before-stale` | `60` | Days of inactivity before an issue becomes stale |
| `days-before-close` | `5` | Days of inactivity before a stale issue is closed |
| `stale-issue-message` | see workflow | Message posted on stale issues |
| `exempt-issue-labels` | see workflow | Comma-separated labels that exempt an issue |
| `exempt-draft-pr` | `true` | Exempt draft PRs from being marked stale |
