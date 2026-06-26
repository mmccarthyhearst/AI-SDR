# Practical Agent Workflow Guide

This guide translates the repository scaffold into a concrete operating plan.

## 1. What You Are Looking At

The new files are not another application by themselves. They are an **agent operating system for the repository**:

- `AGENTS.md` is the manager. It tells an AI agent how to classify work, which specialist instructions to read, how to hand off intermediate outputs, and what quality bar to meet.
- `agents/*.md` are specialist job descriptions. Each one tells the AI how to behave for a specific role such as researcher, qualifier, router, outreach writer, engineer, QA reviewer, or integration architect.
- `templates/*.md` are standard deliverable shapes. They make outputs consistent enough that your team can review and reuse them.
- `workdir/` is the scratchpad for a multi-step run. One stage can leave a safe artifact there for the next stage to consume.
- `docs/chatgpt-codex-setup.md` explains the technical setup options.

A simple mental model:

```text
User request
   -> AGENTS.md decides who should handle it
   -> agents/<specialist>.md provides role-specific instructions
   -> templates/ provides the output format
   -> workdir/ stores temporary handoffs when needed
   -> Codex, Custom GPT, or middleware performs the actual work
```

## 2. The Most Practical Way To Use It First

Start with **Codex against GitHub** because this requires the least extra infrastructure.

### Pilot Task

Use a small repo task first, not a production sales workflow. For example:

```text
Follow AGENTS.md. Use agents/codex-engineer.md and agents/qa-reviewer.md. Add a small validation improvement to the lead qualification logic, update tests, run the relevant checks, commit the change, and summarize the PR.
```

Why this is the best first test:

- It proves Codex can read the instructions.
- It proves Codex can route itself to the right specialist files.
- It produces a normal GitHub PR that your team already knows how to review.
- It avoids production data, CRM writes, and outbound email risk.

## 3. How To Use It With ChatGPT Enterprise

There are three levels. Do them in this order.

### Level 1: Human-Copied Instructions

Use this immediately, with no engineering work:

1. Open ChatGPT Enterprise.
2. Paste a task plus the relevant agent file content.
3. Ask ChatGPT to produce the deliverable using the matching template.

Best for:

- testing the agent roles,
- refining the templates,
- training your team on the workflow.

Limitation: ChatGPT is not automatically reading GitHub yet.

### Level 2: Custom GPT Reads GitHub

Use this when you want the team to stay inside ChatGPT but pull instructions from the repo.

The Custom GPT should be able to:

1. Read `AGENTS.md`.
2. List `agents/`.
3. Read one or more selected specialist files.
4. Optionally read `templates/`.

Best for:

- account research briefs,
- outbound messaging drafts,
- campaign plans,
- qualification summaries,
- internal sales playbooks.

Limitation: this level is best for text generation and planning. It should not directly send emails, mutate CRM records, or run private scripts.

### Level 3: Custom GPT Calls Middleware

Use this only when the agent needs to execute real work.

The flow is:

```text
ChatGPT Enterprise Custom GPT
  -> calls your FastAPI middleware
  -> middleware reads AGENTS.md and agents/*.md from GitHub
  -> middleware runs approved tools/scripts/internal APIs
  -> middleware returns results to ChatGPT
```

Best for:

- generating files,
- running approved research tools,
- writing to CRM after approval,
- creating calendar links,
- sending Slack notifications,
- enforcing audit logs and human approval gates.

## 4. Recommended 30-Day Rollout

### Week 1: Prove The Pattern

- Use Codex on one engineering task.
- Use ChatGPT manually with `agents/researcher.md` and `templates/research_brief.md` for one account research brief.
- Edit the agent files based on what felt unclear.

### Week 2: Standardize One Sales Workflow

Pick one repeatable workflow, such as:

```text
Research 10 QSR franchise accounts -> qualify them -> route them -> draft first-touch outreach.
```

Use these files:

- `agents/pipeline-orchestrator.md`
- `agents/researcher.md`
- `agents/lead-qualifier.md`
- `agents/lead-router.md`
- `agents/outreach-specialist.md`
- `templates/research_brief.md`
- `templates/qualification_summary.md`
- `templates/routing_summary.md`
- `templates/outreach_package.md`

### Week 3: Create The Custom GPT

Build a Custom GPT for non-engineering users.

Suggested name:

```text
AI-SDR Campaign Orchestrator
```

Suggested instruction:

```text
You are the AI-SDR Campaign Orchestrator. For every request, read AGENTS.md from the configured GitHub repository, classify the task, then read the relevant specialist files in agents/. Use templates/ for deliverables. If the task requires code execution, CRM writes, email sending, private tools, or long-running jobs, explain that middleware or human approval is required before execution.
```

### Week 4: Decide Whether Middleware Is Worth It

Only build middleware if the workflow needs one or more of these:

- private API calls,
- generated files,
- CRM writes,
- email sending,
- calendar scheduling,
- audit logs,
- approvals,
- long-running tasks.

If your team mainly needs plans, briefs, and drafts, the Custom GPT plus GitHub-readable Markdown may be enough.

## 5. Concrete Example Prompts

### Codex Engineering Prompt

```text
Follow AGENTS.md. Use agents/codex-engineer.md and agents/qa-reviewer.md. Review the lead qualification tests, identify one missing edge case, add the test and implementation if needed, run the relevant checks, commit, and prepare a PR summary.
```

### ChatGPT Enterprise Research Prompt

```text
Use the AI-SDR agent workflow. Read the researcher instructions and the research brief template. Build a research brief for regional QSR franchise groups in the United States with 5+ units that may need operational reporting automation. Do not invent facts; separate confirmed facts from assumptions.
```

### Custom GPT Campaign Prompt

```text
Run the pipeline workflow for a QSR franchise campaign. Use the pipeline orchestrator, researcher, lead qualifier, lead router, and outreach specialist roles. Produce a research brief, qualification summary, routing summary, and outreach package. Do not send messages or update CRM.
```

### Middleware-Backed Prompt

```text
Run an approved SDR workflow for the QSR franchise segment. Research accounts, score fit, create outreach drafts, and prepare CRM payloads for human review. Do not send email or write to CRM until approval is granted.
```

## 6. Success Criteria

You know this system is working when:

- agents consistently read `AGENTS.md` first,
- outputs follow the templates,
- sales workflows produce reviewable artifacts,
- engineering workflows produce reviewable PRs,
- risky external actions require human approval,
- improvements to one Markdown file improve the workflow for everyone.
