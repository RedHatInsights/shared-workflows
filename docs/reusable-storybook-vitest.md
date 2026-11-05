# Reusable Storybook Vitest Workflow

The target for Storybook 10 + Vite consumers is
`reusable-storybook-vitest.yml`: a standalone Storybook build and an independent
Vitest browser-test job. Both jobs always run; this workflow has no test opt-out.
The existing [Chromatic upload and PR-link workflow](reusable-chromatic.md) stays
in place. **Preserving the build artifact alone is not sufficient.**

The [legacy workflow](reusable-storybook.md) remains unchanged while existing
callers migrate. New and migrating consumers use this Vitest workflow. Once the
legacy callers have moved, retire their old runner in a separately reviewed
compatibility change; two runners are not the long-term standard.

## Consumer prerequisites

- Storybook 10 with `@storybook/react-vite` and `@storybook/addon-vitest`.
- A Vitest project named `storybook`, using `@vitest/browser-playwright`, with
  browser mode enabled, `headless: true`, and a Chromium instance.
- `npm run test:storybook` executes `vitest run --project=storybook` and fails
  when assertions fail or no tests are discovered. Do not enable
  `passWithNoTests`, swallow failures, or exclude stories to make CI green.
- `npm run build-storybook` produces the distributable in `storybook-static`
  unless the build command and directory inputs are changed together.
- A committed `package-lock.json`. Both jobs use `npm ci`; keep the local
  Playwright CLI compatible with the browser provider's resolved dependency.
- Node.js 22.12+ on Node 22 (the default `22` selects the current Node 22 release),
  or another Node release supported by the consumer's dependencies.

Keep the consumer's providers, interaction assertions, MSW isolation, console
failure policy, and intentional coverage policies. Repair missing mocks rather
than weakening production behavior or introducing new skips.

## Usage

In the consumer's `.github/workflows/storybook.yml`:

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
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook-vitest.yml@master
```

Use the consumer's actual target branches. Preserve existing caller concurrency,
lint jobs, and other checks when replacing duplicated build/test steps. In
particular, a reusable-workflow caller must not remove repository-specific checks
for forbidden story patterns, `.only`, or skip tags.

The workflow executes the caller's proposed PR revision using ordinary checkout.
Do not use `pull_request_target` to execute untrusted PR content with credentials.
Fork-workflow approval remains subject to the repository's security policy.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `node-version` | string | `22` | Supported Node.js version for both jobs |
| `build-command` | string | `npm run build-storybook` | Command producing the standalone Storybook build |
| `storybook-dir` | string | `storybook-static` | Filesystem directory uploaded by the build job |
| `artifact-name` | string | `storybook-static` | Artifact name; must match the Chromatic caller |

The test entry point is deliberately fixed at `npm run test:storybook`. There is
no `test-command` or `run-tests` input and no legacy runner mode. Adapt the
consumer's package script and Vitest configuration instead of starting a static
Storybook server or appending the old runner's `--url` argument.

For a custom build location:

```yaml
jobs:
  storybook:
    uses: RedHatInsights/shared-workflows/.github/workflows/reusable-storybook-vitest.yml@master
    with:
      build-command: npm run build-storybook -- --output-dir dist/storybook
      storybook-dir: dist/storybook
      artifact-name: storybook-dist
```

Nested filesystem directories are supported. Artifact names must satisfy
GitHub's artifact naming restrictions, including no slashes. The build fails if
there are no files to upload.

### Required permissions and secrets

The Storybook caller needs only:

```yaml
permissions:
  contents: read
```

No Chromatic token, staging credentials, or PR-write permission is needed to
build or execute browser tests. Checkout does not persist credentials. The
separate Chromatic publisher retains its own permissions and project token.

## Chromatic publication and PR links are mandatory

**Do not remove or disable the existing Chromatic caller when migrating the
Storybook workflow.** Preserve the full flow:

1. Build the intended PR revision and upload its Storybook artifact.
2. Publish that artifact to Chromatic with the correct commit/branch metadata.
3. Post or update the PR comment containing the working Storybook preview and
   Chromatic build links.

Keep the producer caller's workflow `name: Storybook` if that is the name the
publisher already watches. If a consumer uses a different name, retain it or
update its matching `workflow_run.workflows` selector deliberately. Preserve the
artifact name, or change `artifact-name` in **both** callers. The publisher
continues to download the artifact from the triggering run ID, not an arbitrary
latest build.

An existing consumer can retain this separate Chromatic caller:

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

For a custom artifact name, also set the Chromatic job's
`with.artifact-name: storybook-dist`. Changing `storybook-dir` alone does not
change the artifact name or require a publisher directory change.

The existing publisher's success/event guard, fork-safe checkout, triggering-run
artifact selection, metadata, concurrency, and PR-comment upsert remain intact.
A failed Storybook workflow does not publish under that existing success guard;
this migration does not change the publication policy. Do not give the test job
publication secrets to work around fork restrictions.

The shared `reusable-chromatic.yml` is not changed by this rollout foundation.
Governance's separate Chromatic workflow is also outside the cleanup scope and
must remain untouched.

### End-to-end publication verification

For every migrated consumer, attach evidence of:

- A successful Storybook build and interaction-test run on a PR.
- A successful Chromatic upload using that PR's artifact and revision.
- The actual PR comment with an accessible preview link and build link. A
  workflow run URL or artifact download URL alone is not this acceptance proof.
- A later successful PR revision updating the comment/preview correctly, with
  the existing concurrency policy preventing stale duplicate publications.

Workflow linting and an artifact on disk do not establish that the upload or
PR-link reporting still works. Keep this verification outstanding until the
hosted runs can be observed; do not invent success from a local build.

## Build, test, and merge enforcement

The reusable jobs have stable names `build` and `test`. They have no dependency
on each other, so a broken bundle build cannot cause the test job to be silently
skipped. Each job installs its own dependencies and has a 30-minute timeout.
The test job installs only Chromium using the already installed Playwright CLI
(`npx --no-install`), then runs the suite directly through Vitest. It does not
download the build artifact or start a static Storybook server; Vitest manages
its own browser harness.

With the example caller job ID `storybook`, the expected reusable job display
names are `storybook / build` and `storybook / test`. An authorized administrator
must observe their actual PR check contexts/app identity and require **both**,
or introduce a separately validated aggregate that fails unless both succeed.
Requiring only the test result leaves build failures unenforced. Retain the
required Konflux check as well, after verifying it actually includes this suite.

Do not infer enforcement from YAML presence or a green Chromatic upload.
Validate assertion failures, build failures, skipped/cancelled results, branch
and path filters, fork approvals, and any merge-queue configuration before
setting required checks. Repository-rule changes are separate administrator work.

## Konflux: the same suite, not a replacement

GitHub Actions intentionally runs the suite for accessible feedback, while
Konflux **also** runs the identical `npm run test:storybook` script. The Konflux
rollout remains tracked by RHCLOUD-52437. Calling a reusable Actions workflow
does not configure Konflux by itself.

A consumer's supported browser-capable Konflux task/container can use:

```bash
set -euo pipefail
npm ci
npx --no-install playwright install chromium
npm run test:storybook
```

Use an approved Playwright browser image with the required OS libraries, or
provide those libraries through the supported pipeline setup. The image's
preinstalled browser revision may not match the lockfile: install the revision
resolved by the local CLI, or provision that exact browser in an approved image.
The installation recipe requires an environment that permits dependency/browser
downloads; a hermetic task needs those assets prepared in advance.

Do not put browser tests into a browserless hermetic unit-test task. Preserve
application E2E tests, but make Storybook execution independent of stage
credentials, application startup, and E2E skip flags. Ensure the task propagates
the suite's exit status and retains useful logs. Coordinate missing shared
pipeline capabilities under the Konflux rollout rather than declaring a
unit-only green pipeline sufficient.

## Validation and rollout

Local contract checks use the repository's existing Python dependency, PyYAML:

```bash
python3 .github/scripts/test_storybook_workflow.py --workflow /path/to/reusable-storybook-vitest.yml -v
actionlint /path/to/reusable-storybook-vitest.yml
```

After the workflow is installed in its final location, omit `--workflow` to use
`.github/workflows/reusable-storybook-vitest.yml`.

Before promoting consumer migrations:

1. Review the additive shared workflow and record the reviewed revision. Existing
   legacy callers keep their old behavior; a command override is not a runner
   migration. Indexed code search is not a complete inventory of pinned, fork,
   or non-default-branch callers.
2. Validate a real SB10/Vite consumer locally: install locked dependencies and
   Chromium, execute the story suite, and build Storybook separately.
3. Demonstrate that a deliberate play assertion failure fails the test command,
   that no tests discovered fails, and that a deliberately broken build fails.
   Remove deliberate failures; never keep skips or relaxed policies to get green.
4. Use the User Preferences pilot to observe hosted build/test checks, the
   corresponding Konflux result, and the full Chromatic upload/PR-link path.
   Local contract tests cannot prove hosted checkout, permissions, or check names.
5. Only after the reviewed foundation and pilot are validated, activate dependent
   migrations. Admin enforcement and eventual legacy-workflow removal are
   separate coordinated steps.
