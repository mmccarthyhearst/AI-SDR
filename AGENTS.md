# AGENTS.md - AI-SDR Orchestrator

This repository is set up for a folder-based agent orchestration workflow that can be used by Codex, ChatGPT Enterprise workflows, GitHub-hosted automation, and human operators.

## Purpose

Use this file as the project-level orchestrator. It explains how to route work to specialist agent instruction files in `agents/`, how to share intermediate work through `workdir/`, and how to preserve repeatable operating standards for the AI-SDR application.

## Repository Context

AI-SDR is an autonomous sales development representative system focused on franchise-oriented outbound workflows. The application includes API services, CrewAI-style agent code, CRM/email/calendar/slack tools, and test coverage for sourcing, qualifying, routing, outreach, and pipeline operations.

## Common User Interfaces

Use the same repository instructions from any of these interfaces:

1. **ChatGPT Codex / Codex Cloud**: connect the GitHub repository, open a task, and ask Codex to follow `AGENTS.md`.
2. **ChatGPT Enterprise Custom GPT**: configure a Custom GPT Action or middleware endpoint that reads this repository and dispatches tasks according to this file.
3. **GitHub UI / Pull Requests**: ask an AI coding agent to make changes against this repo and require it to follow this orchestrator.
4. **Local CLI / IDE**: run Codex or another coding agent locally from the repository root.

## Routing Rules

When a task arrives, classify it first, then read the relevant specialist file in `agents/`.

| Task Type | Primary Agent | When to Use |
| --- | --- | --- |
| Repository changes, architecture, API, tests, PR prep | `agents/codex-engineer.md` | Code implementation, debugging, refactors, test fixes, CI readiness |
| Multi-step SDR pipeline planning and execution | `agents/pipeline-orchestrator.md` | End-to-end lead sourcing, qualification, routing, outreach coordination |
| Market, franchise, account, or competitor research | `agents/researcher.md` | Gathering evidence, lead/account context, buying signals, source summaries |
| ICP scoring and lead qualification | `agents/lead-qualifier.md` | Fit scoring, tiering, qualification rationale, buying-signal analysis |
| Territory, rep, or team assignment | `agents/lead-router.md` | Routing decisions, land-and-expand flags, sales ownership logic |
| Email, LinkedIn, and appointment messaging | `agents/outreach-specialist.md` | Personalized outreach copy, booking flows, rep handoff notes |
| ChatGPT Enterprise / Custom GPT / middleware setup | `agents/integration-architect.md` | GitHub Actions, FastAPI middleware, Custom GPT Actions, API schemas |
| QA, security, privacy, and release checks | `agents/qa-reviewer.md` | Test plans, regression checks, PII review, deployment readiness |

## Orchestration Loop

For complex tasks, follow this loop:

1. **Intake**: restate the user request, identify deliverables, and list assumptions.
2. **Route**: choose one or more specialist files from `agents/` and read them before acting.
3. **Plan**: create a short task plan with dependencies and expected artifacts.
4. **Execute**: complete the work. For multi-agent style work, save handoff artifacts in `workdir/` using descriptive names.
5. **Review**: run relevant tests or checks. If tests cannot run because of environment limits, document the limitation.
6. **Package**: summarize changes, cite files, and prepare a pull request when code or repository files changed.

## Handoff Convention

Use `workdir/` as the shared workspace for generated outputs that are useful during an orchestration run.

Recommended naming:

- `workdir/research_<topic>_<YYYYMMDD>.md`
- `workdir/qualification_<segment>_<YYYYMMDD>.md`
- `workdir/routing_<campaign>_<YYYYMMDD>.md`
- `workdir/outreach_<campaign>_<YYYYMMDD>.md`
- `workdir/release_check_<change>_<YYYYMMDD>.md`

Do not commit sensitive generated artifacts, private customer data, credentials, raw exports, or PII into `workdir/`.

## Development Standards

- Use Python 3.11+ conventions and follow the project configuration in `pyproject.toml`.
- Keep code and tests aligned with the existing `src/ai_sdr/` and `tests/` structure.
- Prefer small, reviewable changes with clear commit messages.
- Never add secrets, API keys, customer PII, or private tokens to the repository.
- Do not wrap imports in `try`/`except` blocks.
- Use existing service, schema, model, and tool boundaries before creating new abstractions.

## Testing Expectations

Run the most relevant checks for any change:

- `python -m pytest` for full test coverage when dependencies are available.
- `python -m pytest tests/unit` for focused unit checks.
- `python -m ruff check .` for linting when ruff is installed.
- Add or update tests when behavior changes.

## ChatGPT Enterprise + Codex Setup Summary

1. Store this repo in GitHub.
2. Connect the repo to ChatGPT Codex or your Enterprise GitHub connector.
3. Tell Codex: “Follow `AGENTS.md`; use the relevant specialist files in `agents/`; create a branch and PR.”
4. For a Custom GPT, expose either:
   - a GitHub Contents API Action that can read `AGENTS.md` and `agents/*.md`, or
   - a middleware API that reads this repo, runs tools, and returns final artifacts.
5. Use `docs/chatgpt-codex-setup.md` for the detailed setup path.
6. Use `docs/practical-agent-workflow.md` for a plain-English rollout plan and example prompts.

## Done Criteria

A task is complete when:

- The requested artifact or code change exists.
- Relevant specialist instructions were followed.
- Tests/checks were run or limitations were documented.
- The final response explains what changed and where.
- For repository changes, the work is committed and a pull request summary is prepared.
