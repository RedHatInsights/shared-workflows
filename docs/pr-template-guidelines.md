# PR Template Guidelines

Rules and conventions for creating and maintaining pull request templates in `pr-templates/`.

## Template Organization

### Directory Structure

```
pr-templates/
  README.md         # Which template to use, adoption instructions
  frontend.md       # UI applications, React components
  backend.md        # APIs, services, server-side logic
  infra.md          # CI/CD, shared tooling, build configs
```

### Template Categories

| Template | Target repos | Key sections |
|----------|-------------|--------------|
| `frontend.md` | React/PatternFly UI apps | Screenshots (before/after), accessibility checklist |
| `backend.md` | Go/Python/Node.js APIs | Local test steps, API spec, migrations, security checklist |
| `infra.md` | Workflows, operators, build tools | Blast radius, rollback plan, consumer testing |

Choose the template by the **type of change**, not the repo name. A CI config change in a frontend repo should use the infra template.

## Template Conventions

### Required Sections

Every template must include:

1. **Description** — What and why, with a Jira ticket link placeholder: `[RHCLOUD-XXXXX](https://issues.redhat.com/browse/RHCLOUD-XXXXX)`
2. **A context-specific section** — Screenshots for frontend, local test steps for backend, blast radius for infra
3. **Checklist** — Category-specific items as `- [ ]` checkboxes
4. **AI disclosure** — Standard comment block for noting AI tool usage

### Writing Style

- Use HTML comments (`<!-- ... -->`) for instructions to the PR author — these are invisible in the rendered PR
- Keep checklists actionable: each item should be a yes/no verification, not a vague instruction
- Mark optional checklist items with `_(Optional)_` prefix
- Use `---` horizontal rules to visually separate sections

### Jira Link Pattern

Always include the Jira link at the top of the Description section:

```markdown
[RHCLOUD-XXXXX](https://issues.redhat.com/browse/RHCLOUD-XXXXX)
```

### AI Disclosure Block

Every template ends with:

```markdown
### AI disclosure
<!-- If AI tools contributed, note them. E.g.: Assisted by: Claude Code -->
```

## Adoption by Consuming Repos

Templates in `pr-templates/` are **reference copies** — GitHub does not apply them automatically from this location. Each consuming repo must:

1. Copy the chosen template to `.github/PULL_REQUEST_TEMPLATE.md` in their repo
2. Commit and push — GitHub will pre-fill new PRs with the template

See `pr-templates/README.md` for detailed adoption instructions.

## Modifying Templates

- Changes here affect all future adoptions but NOT repos that have already copied the template
- Breaking changes or significant restructuring should be communicated to consuming teams
- Keep templates concise — a long template discourages use
- Test rendering on GitHub before merging (preview in a draft PR)
