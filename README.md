# AI-SDR Agent Orchestration Starter

This repository now contains two related systems:

1. **The AI-SDR application** in `src/ai_sdr/`, which is the Python sales development representative app.
2. **The agent orchestration layer** in `AGENTS.md`, `agents/`, `templates/`, and `workdir/`, which tells Codex, ChatGPT Enterprise, a Custom GPT, or another AI coding/workflow agent how to operate this repo consistently.

If you are wondering “what am I looking at?”, the short answer is:

> This repo is being turned into a GitHub-hosted operating manual for an AI agent team. `AGENTS.md` is the manager, `agents/*.md` are the role descriptions, `templates/*.md` are output formats, and `workdir/` is the temporary handoff area.

## What Each Folder Is For

| Path | What It Is | How You Use It |
| --- | --- | --- |
| `AGENTS.md` | The top-level orchestrator | Tell Codex or another repo-aware agent to start here before doing work. |
| `agents/` | Specialist agent instructions | Add or edit role files such as researcher, qualifier, router, outreach, engineer, QA, and integration architect. |
| `templates/` | Standard output formats | Use these when an agent produces a research brief, qualification summary, routing summary, or outreach package. |
| `workdir/` | Temporary shared workspace | Store non-sensitive intermediate handoffs during a multi-step run. Generated artifacts are ignored by git by default. |
| `docs/chatgpt-codex-setup.md` | Setup guide | Use this to connect the pattern to ChatGPT Codex, a Custom GPT, or middleware. |
| `docs/practical-agent-workflow.md` | Practical action guide | Start here when deciding what to do next and how to roll this out to a team. |

## Recommended First Use

Start with ChatGPT Codex or a repo-aware coding agent and give it a small, concrete task:

```text
Follow AGENTS.md. Read the relevant specialist files in agents/. Improve the lead qualification workflow for franchise prospects. Make the smallest useful change, run relevant checks, commit, and summarize the PR.
```

This validates that the repository instructions are discoverable and that the agent follows your preferred workflow.

## Recommended Rollout Path

1. **Use this with Codex first.** Codex is the simplest practical interface because it can read the repo, edit files, run checks, commit, and prepare PRs.
2. **Then create a Custom GPT for non-engineering workflows.** Have it read `AGENTS.md` and `agents/*.md` through a GitHub Action/API integration so your team can ask for research briefs, outreach packages, and routing plans from ChatGPT Enterprise.
3. **Only add middleware when you need execution.** A FastAPI middleware service is useful when the Custom GPT must run private tools, generate files, call CRM/email/calendar APIs, or enforce approval workflows.

## What Not To Do Yet

- Do not connect production CRM, email, or calendar systems until you have human approval gates.
- Do not commit customer exports, credentials, API keys, or PII.
- Do not treat the Markdown agent files as magic. They are reusable instructions. Real execution still happens through Codex, a Custom GPT action, middleware, or the existing AI-SDR app.

## Next Practical Step

Read `docs/practical-agent-workflow.md`, then choose one pilot workflow:

- engineering changes with Codex,
- franchise account research in a Custom GPT,
- or middleware-backed SDR execution.
