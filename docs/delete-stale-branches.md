# Delete Stale Branches

Deletes remote branches with no commits newer than a configurable age. Safe by default — runs in dry-run mode unless explicitly disabled.

## Usage

```yaml
name: Delete stale branches

on:
  schedule:
    - cron: "17 3 * * 1"  # Weekly Monday 3:17am UTC
  workflow_dispatch:
    inputs:
      dry-run:
        description: "Dry run (no deletions)"
        type: boolean
        default: true

permissions:
  contents: write

jobs:
  cleanup:
    uses: RedHatInsights/shared-workflows/.github/workflows/delete-stale-branches.yml@master
    with:
      dry-run: ${{ github.event_name == 'schedule' && false || inputs.dry-run }}
```

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `days-before-stale` | `number` | `90` | Branches with no commits newer than this are deleted |
| `protected-patterns` | `string` | `main,master,release/*,hotfix/*,konflux/references/*` | Comma-separated branch name patterns to never delete (fnmatch globs) |
| `dry-run` | `boolean` | `true` | Log what would be deleted without actually deleting |

## Required Permissions

Callers must set:

```yaml
permissions:
  contents: write
```

## Protected Branches

The following branches are always protected:

- The repo's default branch (auto-detected)
- `main`, `master`
- `release/*`, `hotfix/*`
- `konflux/references/*`

Override with the `protected-patterns` input:

```yaml
with:
  protected-patterns: "main,master,release/*,hotfix/*,konflux/references/*,staging"
```

> **Note on Konflux**: `konflux/mintmaker/*` branches (automated dependency PRs) are intentionally not protected — they're the primary source of stale branch buildup. If your repo uses `konflux/references/*` or other persistent `konflux/` branches, add them to `protected-patterns`.

## Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `TOKEN` | No | PAT or GitHub App token with permission to delete branches. Falls back to the default `GITHUB_TOKEN` if not provided. |

## Branch Rulesets

If your repo has rulesets that restrict branch deletion, the default `GITHUB_TOKEN` will be denied even with `contents: write`. Options:

1. **Pass a privileged token**: Set an org-level secret (e.g., `BRANCH_CLEANUP_TOKEN`) from a user or GitHub App that has bypass permissions on the ruleset, and pass it via `secrets`:
   ```yaml
   jobs:
     cleanup:
       uses: RedHatInsights/shared-workflows/.github/workflows/delete-stale-branches.yml@master
       with:
         dry-run: false
       secrets:
         TOKEN: ${{ secrets.BRANCH_CLEANUP_TOKEN }}
   ```
2. **Add a bypass actor**: In your repo's ruleset settings, add `github-actions[bot]` as a bypass actor for the branch deletion restriction.
3. **Do nothing**: The workflow logs a warning for each branch it cannot delete and continues. Dry-run mode still works regardless of rulesets.

## How It Works

1. Fetches all remote branches with their last commit date
2. Skips the default branch and any branch matching a protected pattern
3. Skips branches with commits newer than `days-before-stale`
4. In dry-run mode: logs candidates to the workflow step summary
5. Otherwise: deletes each stale branch via `git push origin --delete`
6. Posts a summary table to the GitHub Actions step summary
