# Stale

## Usage

```yml
name: Handle stale issues and PRs

on:
  schedule:
    - cron: "30 1 * * *" 

jobs:
  stale:
    uses: RedHatInsights/shared-workflows/.github/workflows/stale.yml@master
```
