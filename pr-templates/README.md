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

Copy the appropriate template into your repository as `.github/PULL_REQUEST_TEMPLATE.md`, or configure [multiple templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository#adding-a-pull-request-template) if your repo spans categories.
