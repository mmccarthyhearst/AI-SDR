# ChatGPT Enterprise and Codex Setup

This guide explains how to use the repository-based agent orchestration system from ChatGPT Enterprise, ChatGPT Codex, GitHub, or a middleware service.

## Goal

The repository acts as the source of truth for your AI team:

- `AGENTS.md` is the team lead and routing layer.
- `agents/*.md` are specialist role instructions.
- `templates/*.md` are shared deliverable formats.
- `workdir/` is the temporary handoff area for multi-step runs.

## Option 1: Run Directly in ChatGPT Codex

Use this when you want Codex to make repository changes, run checks, commit code, and prepare pull requests.

1. Push this repository to GitHub.
2. In ChatGPT Enterprise, connect the GitHub integration for the workspace or user account that will run Codex.
3. Grant access only to the repositories Codex needs.
4. Open Codex and select this repository.
5. Start a task with an instruction like:

   ```text
   Follow AGENTS.md. Use the relevant specialist files in agents/. Implement the requested change on a new branch, run relevant checks, commit, and prepare a PR summary.
   ```

6. Review the diff, test output, commit, and pull request before merging.

## Option 2: Custom GPT Reads the Repository

Use this when your team wants to stay inside a Custom GPT and the workflow mostly needs to read instructions, route tasks, and produce text artifacts.

Recommended Action capabilities:

- Read `AGENTS.md`.
- List files in `agents/`.
- Read selected `agents/*.md` files.
- Optionally read templates in `templates/`.

A Custom GPT can call the GitHub Contents API for these operations. For private repositories, use least-privilege authentication, preferably a GitHub App or tightly scoped token managed by your enterprise admin.

Custom GPT instruction pattern:

```text
For every task, first read AGENTS.md from the configured GitHub repository. Classify the task, then read the relevant specialist file from agents/. Follow the specialist instructions and use templates/ when producing deliverables. If the task requires code execution, file generation, private tools, or long-running work, call the middleware action instead of trying to complete it only in chat.
```

## Option 3: Custom GPT Calls Middleware

Use this when the Custom GPT needs real execution: running scripts, calling private APIs, creating files, searching approved sources, or enforcing enterprise audit controls.

Basic architecture:

```text
ChatGPT Enterprise Custom GPT
        |
        | HTTPS Action request
        v
FastAPI Middleware
        |
        | reads AGENTS.md and agents/*.md from GitHub
        | runs approved tools / code / internal APIs
        v
Result returned to ChatGPT
```

Minimal endpoint plan:

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Confirms the middleware is online |
| `POST /agent-task` | Accepts a user task, task type, repository ref, and optional inputs |
| `GET /runs/{run_id}` | Returns run status and artifact links for longer jobs |

Example request body:

```json
{
  "task": "Build a QSR franchise lead research brief and draft first-touch outreach.",
  "task_type": "pipeline",
  "repo": "your-org/ai-sdr",
  "ref": "main",
  "inputs": {
    "segment": "QSR franchises",
    "geo": "United States"
  }
}
```

Middleware responsibilities:

1. Validate the caller and requested repository.
2. Fetch `AGENTS.md` and relevant `agents/*.md` files.
3. Choose an execution plan.
4. Run approved tools or scripts.
5. Store safe artifacts.
6. Return a concise result and links to artifacts.

## Recommended Rollout Plan

1. Start with Codex direct against this repository for engineering workflows.
2. Add a Custom GPT that can read `AGENTS.md` and `agents/*.md` for non-engineering users.
3. Add middleware only after you know which workflows require execution beyond chat.
4. Add audit logs, role-based access, and approval gates before connecting production CRM, email, or calendar systems.

## Security Checklist

- Use least-privilege GitHub access.
- Keep secrets in a vault or platform secret manager.
- Never commit API keys, customer data, raw exports, or PII.
- Require human review before sending external outreach.
- Log high-level decisions and tool calls for auditability.
- Use separate development and production integrations.
