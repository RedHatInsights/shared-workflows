#!/usr/bin/env python3
"""Check the SB10/Vitest workflow and its existing Chromatic artifact contract.

These are local structural regression checks, not a substitute for executing a
consumer's stories or observing hosted Actions, Konflux, and Chromatic runs.
Requires the repository's existing PyYAML dependency.
"""

import argparse
from pathlib import Path
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github/workflows/reusable-storybook-vitest.yml"


def load_workflow(path):
    # BaseLoader leaves GitHub's `on` key and scalar expressions untouched;
    # PyYAML's YAML 1.1 SafeLoader otherwise interprets `on` as a boolean.
    return yaml.load(path.read_text(), Loader=yaml.BaseLoader)


def step_named(job, name):
    return next(step for step in job["steps"] if step["name"] == name)


def walk_mappings(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_mappings(child)


class StorybookWorkflowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = load_workflow(WORKFLOW_PATH)
        cls.jobs = cls.workflow["jobs"]
        cls.inputs = cls.workflow["on"]["workflow_call"]["inputs"]
        cls.chromatic = load_workflow(
            ROOT / ".github/workflows/reusable-chromatic.yml"
        )

    def test_is_reusable_only_without_publication_secrets(self):
        self.assertEqual(set(self.workflow["on"]), {"workflow_call"})
        self.assertNotIn("secrets", self.workflow["on"]["workflow_call"])
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        self.assertEqual(self.workflow["env"]["CI"], "true")

    def test_has_documented_build_inputs_but_no_test_opt_out(self):
        defaults = {
            "node-version": "22",
            "build-command": "npm run build-storybook",
            "storybook-dir": "storybook-static",
            "artifact-name": "storybook-static",
        }
        self.assertEqual(set(self.inputs), set(defaults))
        for name, default in defaults.items():
            with self.subTest(input=name):
                self.assertEqual(self.inputs[name]["type"], "string")
                self.assertEqual(self.inputs[name]["default"], default)
                self.assertTrue(self.inputs[name]["description"])

    def test_build_and_tests_are_independent_and_always_scheduled(self):
        self.assertEqual(set(self.jobs), {"build", "test"})
        for name, job in self.jobs.items():
            with self.subTest(job=name):
                self.assertEqual(job["name"], name)
                self.assertEqual(job["runs-on"], "ubuntu-24.04")
                self.assertEqual(job["timeout-minutes"], "30")
                self.assertNotIn("needs", job)
                self.assertNotIn("if", job)

    def test_each_job_checks_out_the_callers_revision_without_credentials(self):
        for name, job in self.jobs.items():
            with self.subTest(job=name):
                checkout = step_named(job, "Checkout")
                self.assertTrue(checkout["uses"].startswith("actions/checkout@"))
                self.assertEqual(checkout["with"], {"persist-credentials": "false"})

    def test_each_job_sets_up_node_and_installs_locked_dependencies(self):
        for name, job in self.jobs.items():
            with self.subTest(job=name):
                node = step_named(job, "Node setup")
                self.assertTrue(node["uses"].startswith("actions/setup-node@"))
                self.assertEqual(node["with"]["node-version"], "${{ inputs.node-version }}")
                self.assertEqual(node["with"]["cache"], "npm")
                install = step_named(job, "Install dependencies")
                self.assertEqual(install["run"], "npm ci")
                self.assertNotIn("if", install)

    def test_build_uses_the_configured_command(self):
        step = step_named(self.jobs["build"], "Build Storybook")
        self.assertEqual(step["run"], "${{ inputs.build-command }}")
        self.assertNotIn("if", step)

    def test_artifact_contract_matches_the_existing_chromatic_publisher(self):
        upload = step_named(self.jobs["build"], "Upload Storybook Artifact")
        self.assertTrue(upload["uses"].startswith("actions/upload-artifact@"))
        self.assertEqual(upload["with"]["name"], "${{ inputs.artifact-name }}")
        self.assertEqual(upload["with"]["path"], "${{ inputs.storybook-dir }}")
        self.assertEqual(upload["with"]["if-no-files-found"], "error")
        self.assertEqual(upload["with"]["retention-days"], "3")
        chromatic_input = self.chromatic["on"]["workflow_call"]["inputs"]["artifact-name"]
        self.assertEqual(self.inputs["artifact-name"]["default"], chromatic_input["default"])

    def test_tests_install_the_local_chromium_before_running_the_canonical_script(self):
        steps = self.jobs["test"]["steps"]
        browser = step_named(self.jobs["test"], "Install Playwright Chromium")
        test = step_named(self.jobs["test"], "Run Storybook tests")
        install = step_named(self.jobs["test"], "Install dependencies")
        self.assertEqual(browser["run"], "npx --no-install playwright install --with-deps chromium")
        self.assertEqual(test["run"], "npm run test:storybook")
        self.assertLess(steps.index(install), steps.index(browser))
        self.assertLess(steps.index(browser), steps.index(test))
        self.assertNotIn("if", browser)
        self.assertNotIn("if", test)

    def test_tests_do_not_download_or_serve_a_storybook_build(self):
        for step in self.jobs["test"]["steps"]:
            self.assertNotIn("download-artifact", step.get("uses", ""))
            command = step.get("run", "")
            for legacy_fragment in ("--url", "http-server", "wait-on", "test-storybook", "build-storybook"):
                with self.subTest(step=step["name"], fragment=legacy_fragment):
                    self.assertNotIn(legacy_fragment, command)

    def test_failures_are_not_suppressed_and_permissions_are_not_escalated(self):
        for mapping in walk_mappings(self.workflow):
            self.assertNotIn("continue-on-error", mapping)
            command = mapping.get("run", "")
            self.assertNotRegex(command, r"\|\|\s*(?:true|exit\s+0)")
            self.assertNotIn("passWithNoTests", command)
        for job in self.jobs.values():
            self.assertNotIn("permissions", job)

    def test_actions_are_pinned_to_commit_shas(self):
        for job in self.jobs.values():
            for step in job["steps"]:
                if "uses" in step:
                    self.assertRegex(step["uses"], r"^actions/[a-z-]+@[0-9a-f]{40}$")

    def test_legacy_callers_keep_their_existing_runner_contract(self):
        legacy = load_workflow(ROOT / ".github/workflows/reusable-storybook.yml")
        inputs = legacy["on"]["workflow_call"]["inputs"]
        self.assertEqual(inputs["test-command"]["default"], "npm run test-storybook:ci")
        self.assertEqual(inputs["run-tests"]["default"], "true")
        self.assertEqual(inputs["artifact-name"]["default"], "storybook-static")

    def test_chromatic_still_selects_the_triggering_artifact_and_pr_revision(self):
        upload_job = self.chromatic["jobs"]["upload"]
        download = step_named(upload_job, "Download Artifact")
        publish = step_named(upload_job, "Publish to Chromatic")
        self.assertEqual(download["with"]["run-id"], "${{ github.event.workflow_run.id }}")
        self.assertEqual(download["with"]["name"], "${{ inputs.artifact-name }}")
        self.assertEqual(publish["env"]["CHROMATIC_SHA"], "${{ github.event.workflow_run.head_sha }}")
        self.assertEqual(publish["env"]["CHROMATIC_BRANCH"], "${{ github.event.workflow_run.head_branch }}")

    def test_chromatic_still_posts_both_preview_and_build_links_to_the_pr(self):
        jobs = self.chromatic["jobs"]
        self.assertEqual(jobs["comment"]["needs"], ["upload"])
        self.assertEqual(jobs["comment"]["permissions"], {"pull-requests": "write"})
        self.assertEqual(jobs["upload"]["outputs"]["storybookUrl"], "${{ steps.chromatic.outputs.storybookUrl }}")
        self.assertEqual(jobs["upload"]["outputs"]["buildUrl"], "${{ steps.chromatic.outputs.buildUrl }}")
        find = step_named(jobs["comment"], "Find existing comment")
        comment = step_named(jobs["comment"], "Comment on PR")
        self.assertEqual(find["with"]["body-includes"], "<!-- chromatic-build -->")
        self.assertEqual(comment["with"]["edit-mode"], "replace")
        self.assertEqual(comment["with"]["issue-number"], "${{ steps.find-pr.outputs.result }}")
        self.assertIn("${{ needs.upload.outputs.storybookUrl }}", comment["with"]["body"])
        self.assertIn("${{ needs.upload.outputs.buildUrl }}", comment["with"]["body"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=Path, default=WORKFLOW_PATH, help="Workflow draft or installed workflow to validate")
    args, unittest_args = parser.parse_known_args()
    WORKFLOW_PATH = args.workflow.resolve()
    if not WORKFLOW_PATH.is_file():
        parser.error(f"workflow does not exist: {WORKFLOW_PATH}")
    unittest.main(argv=[sys.argv[0], *unittest_args])
