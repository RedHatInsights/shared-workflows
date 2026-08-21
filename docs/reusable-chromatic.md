# Reusable Chromatic Workflow

Uploads a pre-built Storybook to Chromatic for visual regression testing and posts build links as a PR comment.

## Usage

This workflow is triggered via `workflow_run`, not directly. The caller workflow watches for a completed Storybook build and delegates to this reusable workflow.

```yaml
name: Chromatic Upload

on:
  workflow_run:
    workflows: ["Storybook"]
    types: [completed]

concurrency:
  group: chromatic-${{ github.event.workflow_run.head_repository.full_name }}-${{ github.event.workflow_run.head_branch }}
  cancel-in-progress: true

permissions:
  contents: read
  actions: read
  pull-requests: write

jobs:
  chromatic:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-chromatic.yml@master
    secrets:
      chromatic-project-token: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `artifact-name` | string | `storybook-static` | Name of the Storybook build artifact to download |

## Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `chromatic-project-token` | yes | Chromatic project token |

## Required Permissions

Callers must set:

```yaml
permissions:
  contents: read
  actions: read
  pull-requests: write
```

The reusable workflow scopes `pull-requests: write` to the comment job only.

## Concurrency

The reusable workflow does not set its own concurrency group. Callers **must** add a `concurrency` block to avoid duplicate uploads and wasted Chromatic snapshot quota on rapid pushes:

```yaml
concurrency:
  group: chromatic-${{ github.event.workflow_run.head_repository.full_name }}-${{ github.event.workflow_run.head_branch }}
  cancel-in-progress: true
```

## Custom artifact name

When the Storybook workflow uses a non-default `artifact-name`, pass the same value here. `storybook-dir` on the Storybook workflow is independent and does not need to match.

```yaml
jobs:
  chromatic:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-chromatic.yml@master
    with:
      artifact-name: storybook-dist
    secrets:
      chromatic-project-token: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

## Pinning

For stability, pin the reusable workflow to a commit SHA rather than `@master`:

```yaml
uses: RedHatInsights/shared-workflows/.github/workflows/reusable-chromatic.yml@<sha>
```

## How it works

1. **Upload job** — checks out the consuming repo's default branch (trusted `package.json` / Chromatic config), fetches the triggering commit objects for baseline comparison, downloads the Storybook artifact from the triggering workflow run, and publishes to Chromatic. Fork PR sources are never checked out. On push events, changes are auto-accepted as the new baseline.
2. **Comment job** — finds the associated PR from `workflow_run.pull_requests`, falling back to `repos.listPullRequestsAssociatedWithCommit` for fork PRs, and posts or updates a comment with Storybook and Chromatic build links.
