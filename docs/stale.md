# Stale

Marks inactive issues and PRs stale, then closes them after a further grace
period.

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
    uses: RedHatInsights/shared-workflows/.github/workflows/stale.yml@<commit-sha> # master
```

Pin to a full commit SHA so changes to `shared-workflows` cannot affect your
repo without a PR. The trailing `# master` tells Renovate which branch the SHA
tracks — without it (bare SHA or prose comment) the pin is ignored and silently
goes stale. Once `shared-workflows` publishes version tags, replace `# master`
with `# vX.Y.Z`; pins inside this workflow are maintained by `shared-workflows`' own Renovate run.

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `days-before-stale` | `60` | Days of inactivity before an issue becomes stale |
| `days-before-close` | `5` | Days of inactivity before a stale issue is closed |
| `stale-issue-message` | see workflow | Message posted on stale issues |
| `exempt-issue-labels` | see workflow | Comma-separated labels that exempt an issue |
| `exempt-draft-pr` | `true` | Exempt draft PRs from being marked stale |
