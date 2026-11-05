# Legacy Reusable Storybook Workflow

For Storybook 10 + Vite, use the [Vitest workflow](reusable-storybook-vitest.md).
That is the target for new and migrating consumers; this legacy workflow remains
unchanged temporarily so existing callers are not silently broken. Retire it only
after its callers have migrated, not as a second long-term runner standard.

This workflow builds Storybook and optionally runs the legacy
`@storybook/test-runner` against a served build. Overriding `test-command` with a
Vitest command is **not** a migration: the workflow still starts a static server
and appends `--url`. Use the dedicated Vitest workflow instead.

## Usage

```yaml
name: Storybook

on:
  pull_request:
  push:
    branches: [master, main]

jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook.yml@master
```

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `node-version` | string | `22` | Node.js version |
| `build-command` | string | `npm run build-storybook` | Command to build Storybook |
| `test-command` | string | `npm run test-storybook:ci` | Command to run Storybook tests (receives `-- --url http://localhost:6006`) |
| `storybook-dir` | string | `storybook-static` | Output directory for the Storybook build |
| `artifact-name` | string | `storybook-static` | Name of the uploaded Storybook artifact (must not contain `/` or other GitHub artifact-name characters) |
| `run-tests` | boolean | `true` | Whether to run Storybook interaction tests |

## Required Permissions

Callers must set:

```yaml
permissions:
  contents: read
```

## Build-only (no tests)

```yaml
jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook.yml@master
    with:
      run-tests: false
```

## Custom build directory

`storybook-dir` is the filesystem path only. Nested paths are valid. The artifact is still named `storybook-static` unless you also set `artifact-name`.

```yaml
jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook.yml@master
    with:
      storybook-dir: dist/storybook
```

## Custom artifact name

Use a distinct artifact name when multiple Storybook builds share a pipeline. Pass the same value as `artifact-name` to the [reusable Chromatic workflow](reusable-chromatic.md).

```yaml
jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook.yml@master
    with:
      artifact-name: storybook-dist
```

## Pairing with Chromatic

This workflow produces an artifact named `storybook-static` by default (override with `artifact-name`) consumed by the [reusable Chromatic workflow](reusable-chromatic.md). Chromatic's `artifact-name` must match this workflow's `artifact-name`. Changing `storybook-dir` alone does not require a Chromatic change.

Migration must preserve the complete existing publication flow, including the
Chromatic upload of the correct PR revision and the preview link posted back to
the PR. Keeping an artifact alone is insufficient. Follow the
[Vitest migration and publication checklist](reusable-storybook-vitest.md#chromatic-publication-and-pr-links-are-mandatory).
