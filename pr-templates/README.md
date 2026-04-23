# PR Templates

Canonical pull request templates for HCC Framework repositories. Each template is tailored to the type of repository being changed.

## Which template do I use?

| Template | When to use | Example repos |
|----------|-------------|---------------|
| [Frontend](frontend.md) | UI applications, React components, browser-facing code | insights-chrome, notifications-frontend, widget-layout, astro-virtual-assistant-frontend, insights-advisor-frontend, ocp-advisor-frontend, insights-rbac-ui, patchman-ui, insights-inventory-frontend, insights-remediations-frontend, api-documentation-frontend, user-preferences-frontend, payload-tracker-frontend, malware-detection-frontend, vuln4shift-frontend, scheduler-ui, frontend-starter-app |
| [Backend](backend.md) | APIs, services, server-side logic, data processing | chrome-service-backend, widget-layout-backend, pdf-generator, insights-rbac, astro-virtual-assistant-v2, hcc-ai-assistant, frontend-asset-proxy |
| [Infra](infra.md) | CI/CD workflows, shared tooling, build configs, container images, deployment configs | shared-workflows, frontend-operator, frontend-components, frontend-development-proxy, insights-frontend-builder-common, caddy-ubi, cypress-e2e-image, javascript-clients, frontend-assets, frontend-test-utils, valpop |

> **Not sure?** Pick the template closest to the _type of change_ you're making, not the repo name. A CI config change in a frontend repo should use the Infra template.

## How to adopt

> **These templates are reference copies, not active GitHub templates.** Because they live in `pr-templates/` (not `.github/`), GitHub does not apply them automatically. Each team must manually copy the template they need into their own repository.

### Steps

1. Choose the template that matches your repo (see table above).
2. Copy the file contents into your repository at `.github/PULL_REQUEST_TEMPLATE.md`.
   ```bash
   # Example: adopt the frontend template
   curl -sL https://raw.githubusercontent.com/RedHatInsights/shared-workflows/main/pr-templates/frontend.md \
     -o .github/PULL_REQUEST_TEMPLATE.md
   ```
3. Commit and push. GitHub will pre-fill new PRs with your chosen template.
4. If your repo spans categories, configure [multiple templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository#adding-a-pull-request-template) instead.

> **Future improvement:** A GitHub Actions workflow or sync script could automate distributing template updates to consuming repos. For now, manual copy is required.
