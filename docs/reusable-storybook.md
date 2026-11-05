# Reusable Storybook Workflow

Builds Storybook for publication and runs the repository's test command. The
workflow does not require a particular test runner.

## Self-contained test commands

Use `serve-storybook: false` when the test command owns its environment:

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
    with:
      serve-storybook: false
      test-command: npm run test:storybook
```

Use the consumer's actual target branches and preserve existing concurrency,
lint, and other checks. The `test:storybook` script must run non-interactively,
clean up any server it starts, and exit nonzero on failure or no tests discovered.
It can invoke Vitest directly or wrap a server and another runner. No server is
started by the workflow and no arguments are appended to the command.

The `test-script` job installs locked dependencies and Playwright Chromium, then
executes the command with `CI=true`. It has no dependency on `build`: tests do not
wait for a published build and still run if that build fails. The build job
separately produces the artifact needed for Chromatic. A script that builds
Storybook itself will consequently build it again inside the test job.

At most one test job is selected per caller. Both jobs check out the caller's
revision without persisting credentials. Never execute PR code using a
credentialed `pull_request_target` workflow.

## Existing callers

Defaults are unchanged: the `test` job waits for the build, downloads its
artifact, serves it on port 6006, and appends `-- --url http://localhost:6006` to
`test-command`. Existing callers and custom commands keep this behavior without
changes. Simply replacing the command with Vitest is not enough; also set
`serve-storybook: false`.

This served-build path is temporary compatibility during the consumer rollout,
not a second long-term runner standard. Once callers have migrated, remove it in
a separately reviewed change. SB10/Vite/Vitest remains the rollout's consumer
standard; the shared workflow itself only knows the command contract.

## Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `node-version` | string | `22` | Node.js version supported by the consumer |
| `build-command` | string | `npm run build-storybook` | Command producing the standalone build |
| `test-command` | string | `npm run test-storybook:ci` | Test command; receives `-- --url` only when serving is enabled |
| `serve-storybook` | boolean | `true` | Serve the built artifact; disable for a self-contained test command |
| `storybook-dir` | string | `storybook-static` | Build output directory to upload |
| `artifact-name` | string | `storybook-static` | Artifact name; must match the Chromatic caller |
| `run-tests` | boolean | `true` | Existing build-only opt-out; keep enabled for required story tests |

Both modes require `contents: read`, a committed npm lockfile, and compatible
Node/browser dependencies. The test jobs need no staging credentials, Chromatic
token, or PR-write permissions. Self-contained mode installs Chromium through the
already installed Playwright CLI, not an unpinned downloaded CLI.

For custom build output, change both the command and directory:

```yaml
with:
  serve-storybook: false
  test-command: npm run test:storybook
  build-command: npm run build-storybook -- --output-dir dist/storybook
  storybook-dir: dist/storybook
  artifact-name: storybook-dist
```

Nested directories are supported; artifact names cannot contain slashes. The
build fails if there are no files to upload. Artifacts are retained for three days.

## Preserve Chromatic publication and PR links

**Keep the complete existing Chromatic flow, not just its artifact.** Leave the
[separate Chromatic caller](reusable-chromatic.md) in place and preserve:

- Its `workflow_run` selector: keep the producer's existing workflow name, or
  update the matching selector deliberately.
- The artifact name in both callers. Changing `storybook-dir` alone does not
  change the artifact name.
- Upload of the triggering PR revision and artifact, followed by a PR comment
  containing accessible Storybook preview and Chromatic build links.
- Existing revision metadata, fork/security handling, concurrency, and comment
  updates on later successful revisions.

The reusable Chromatic workflow is unchanged. Its success guard still prevents
publication after a failed Storybook workflow. Governance's separate Chromatic
workflow is outside this change and must also remain untouched.

## Validation and merge checks

Run `actionlint .github/workflows/reusable-storybook.yml`, then exercise the
workflow from a consumer PR. Verify passing tests and build, deliberate assertion
and build failures, and empty test discovery. Keep providers, MSW isolation,
console policies, assertions, and intended coverage; do not add skips or swallow
failures to obtain green.

For self-contained callers, an administrator must observe and require the actual
`storybook / build` and `storybook / test-script` check contexts (with the example
caller ID). The legacy `storybook / test` job is intentionally skipped in this
mode: do not require it instead of the real test result. Keep `run-tests: true`
and verify skipped/cancelled results, branch filters, forks, and merge queues do
not create merge loopholes. Repository-rule changes are separate admin work.

Also verify the full live Chromatic upload and PR-link update on the consumer PR.
A local build or green static lint is not proof of publication.

## Konflux and rollout

Konflux must run the same `npm run test:storybook` command as Actions, in a
supported browser-capable task/container. Install the lockfile-matching Chromium
revision and provide its required OS libraries; a browserless unit-test task is
not sufficient. Preserve application E2E tests, but do not make Storybook depend
on their credentials, startup, or skip flags. RHCLOUD-52437 remains applicable.

Review the shared revision first, then validate the User Preferences pilot in
Actions, Konflux, and Chromatic before activating dependent migrations. Pin or
reference only reviewed revisions according to the consumer's policy. This
workflow change does not itself provision Konflux, enforce merge checks, or
activate downstream tickets.
