# Reusable Storybook Workflow

Builds Storybook for publication and runs `npm run test:storybook`. The repository
owns test setup and cleanup; the shared workflow does not start a server or add
URL arguments. The `build` and `test` jobs run independently.

## Usage

```yaml
name: Storybook

on:
  pull_request:
  push:
    branches: [master, main]

permissions:
  contents: read

jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook.yml@master
```

Use the consumer's actual target branches and preserve existing concurrency,
lint, and other checks. The repository needs a committed npm lockfile and a
`test:storybook` script that runs non-interactively and returns nonzero when tests
fail or no tests are discovered.

The script owns the complete test lifecycle. It can invoke Vitest directly or
build and serve Storybook, wait for readiness, run another test runner, and clean
up the server. The workflow only installs dependencies and Playwright Chromium,
then executes the command with `CI=true`. Vitest manages its own browser harness;
it does not need a separately served Storybook build.

The separate build produces the artifact needed by Chromatic. A test script that
builds Storybook itself will build it again inside the test job. Build failures
do not prevent tests from running. Both jobs check out the caller's revision
without persisting credentials; neither needs publication or staging secrets.
Never execute PR code using a credentialed `pull_request_target` workflow.

## Migration from the old workflow

**This changes the test command contract.** The old workflow served the built
artifact on port 6006 and appended `-- --url http://localhost:6006`. That setup is
removed, and the default command changes from `npm run test-storybook:ci` to
`npm run test:storybook`.

Before adopting this revision, ensure the repository's command owns any required
build/server lifecycle. A bare legacy test-runner command expecting a server
provided by CI will no longer work. This does not force a runner change: a
self-contained wrapper around the existing runner is sufficient. SB10/Vite/Vitest
remains a separate consumer rollout standard.

Check callers before merging, especially those following `@master`. SHA-pinned
callers retain the old behavior until they update their reference. Indexed code
search alone is not a complete inventory of forks or non-default branches.

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `node-version` | string | `22` | Node.js version supported by the consumer |
| `build-command` | string | `npm run build-storybook` | Command producing the standalone build |
| `test-command` | string | `npm run test:storybook` | Self-contained test command, executed unchanged |
| `storybook-dir` | string | `storybook-static` | Build output directory to upload |
| `artifact-name` | string | `storybook-static` | Artifact name; must match the Chromatic caller |
| `run-tests` | boolean | `true` | Existing build-only opt-out; keep enabled for required story tests |

The test job uses the installed Playwright CLI to install Chromium. Keep that CLI
compatible with the test runner's browser dependency. For a different build
location, change the command and directory together:

```yaml
with:
  build-command: npm run build-storybook -- --output-dir dist/storybook
  storybook-dir: dist/storybook
  artifact-name: storybook-dist
```

Nested directories are supported; artifact names cannot contain slashes. Missing
artifact files fail the build. Artifacts are retained for three days.

## Chromatic publication and PR links

Keep the [separate Chromatic caller](reusable-chromatic.md), its matching producer
workflow name, and the same artifact name in both callers. Changing the build
directory alone does not change the artifact name.

The complete flow remains required: upload the triggering PR revision to
Chromatic and post/update working Storybook preview and build links on that PR.
The reusable Chromatic workflow is unchanged, including its revision metadata,
fork/security handling, concurrency, comment updates, and success guard.
Governance's separate Chromatic workflow is also outside this change.

## Validation and rollout

Run `actionlint .github/workflows/reusable-storybook.yml`, then verify a real
consumer PR: passing tests/build, assertion and build failures, and empty test
discovery. Preserve providers, MSW isolation, console policies, and coverage.
Verify live Chromatic upload and PR-link updates; local lint/builds are not proof
of publication.

An administrator must observe and require the actual `build` and `test` checks
(`storybook / build` and `storybook / test` for the example caller). Keep
`run-tests: true` and verify skipped/cancelled results, filters, fork approvals,
and merge queues do not create merge loopholes. Merge rules are separate work.

### Konflux browser-container recipe

Run this Bash script from the checked-out repository in a dedicated browser task
with a writable workspace. Use an approved, versioned Playwright image compatible
with the lockfile; for example, `mcr.microsoft.com/playwright:v1.59.1-noble` for
Playwright 1.59.1. That image supplies Chromium's OS libraries, so the task does
not need root privileges or an `apt-get` step. Upgrade the image when required by
the resolved browser's OS dependencies.

```bash
set -euo pipefail
export CI=true
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"
mkdir -p storybook-test-results

npm ci 2>&1 | tee storybook-test-results/storybook.log
npx --no -- playwright install chromium 2>&1 | tee -a storybook-test-results/storybook.log
npm run test:storybook 2>&1 | tee -a storybook-test-results/storybook.log
```

The local CLI installs the browser revision resolved by the lockfile into the
writable workspace; it does not assume the image's preinstalled browser matches.
This requires browser/package download access. A hermetic task must have the
matching assets prepared in advance. `pipefail` preserves install/test failures
through `tee`, and `set -e` stops subsequent commands when a step fails.

Output is streamed to the Konflux task log and saved to
`storybook-test-results/storybook.log`. Configure the consumer pipeline's
artifact collector to retain that directory in a `finally` task, including on
failure; a workspace file alone is not durable retention after workspace cleanup.
Consumer task wiring and artifact storage remain separate from this example.

Run the identical `npm run test:storybook` command in Actions and Konflux. Preserve
application E2E tests without making Storybook depend on their credentials or
skip flags. RHCLOUD-52437 remains applicable. Validate the User Preferences pilot
in both environments and Chromatic before activating downstream migrations; this
workflow change does not itself configure Konflux or enforce merge checks.
