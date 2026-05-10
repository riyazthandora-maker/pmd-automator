# PMO Automator — System Map

A hierarchical multi-agent system for automating Project Management Office (PMO) workflows, from project initiation through final deliverable generation.

## Architecture

```
pmd-automator/
├── CLAUDE.md                          # This file — system map and agent coordination rules
├── common/
│   ├── templates/                     # Shared document templates (charter, plan, RACI, etc.)
│   └── validation/                    # Shared validation schemas and rules
├── agents/
│   └── initiation/                    # Agent responsible for project initiation phase
│       └── skills/                    # Discrete skill modules for the initiation agent
├── projects/
│   └── project_alpha/                 # One directory per managed project
│       ├── 00_inbox/                  # Raw inputs: emails, briefs, uploads (unprocessed)
│       ├── 01_raw_archive/            # Immutable copies of original source documents
│       ├── 02_working_docs/           # Active working documents (agent-editable)
│       ├── 03_ai_snippets/            # Intermediate AI-generated content and drafts
│       └── 04_final_deliverables/     # Approved, export-ready outputs
├── state/                             # Persistent agent state, task queues, handoff records
└── tests/                             # Automated tests for agents and validation logic
```

## Agent Roles

| Agent | Location | Responsibility |
|-------|----------|----------------|
| Initiation Agent | `agents/initiation/` | Processes inbox items, extracts requirements, produces project charters |

## Document Flow

```
00_inbox → (initiation agent) → 01_raw_archive (archived original)
                              → 02_working_docs (structured draft)
                              → 03_ai_snippets  (intermediate reasoning)
                              → 04_final_deliverables (on approval)
```

## Conventions

- Agents read from `00_inbox` and `02_working_docs`; they never modify `01_raw_archive`.
- All state transitions are logged to `state/`.
- Templates in `common/templates/` are read-only to agents; copies are made to `02_working_docs/` before editing.
- Validation rules in `common/validation/` apply across all projects.
- Tests in `tests/` must pass before any agent skill is promoted.
