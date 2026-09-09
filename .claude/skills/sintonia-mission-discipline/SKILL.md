---
name: sintonia-mission-discipline
description: Use for any substantial SINTONIA engineering, audit, refactor, integration, Collection, Security, System Map, Scrap, Intelligence, or portal mission. Keeps work focused by using repo authorities instead of repeating them, separating diagnosis from implementation, limiting scope, preserving context, and defining objective evidence for completion.
---

# SINTONIA Mission Discipline

Use this skill whenever the user asks for a substantial mission, a long autonomous task, an architectural audit, a refactor, an integration, a red-team pass, or work expected to continue for hours.

The goal is not to make the mission description long. The goal is to make the execution reliable.

## Core rule

> Long task does not mean long prompt.
>
> Prefer: **short mission → deep execution → strong verification**.

Do not repeat in the mission text what the repository already owns canonically.
Point to the authority, read only the relevant sections, then work against the code.

## 1. First classify the mission

Before acting, choose exactly one primary mode:

- `DIAGNOSE` — establish AS-IS and evidence; no functional edits.
- `PLAN` — produce the smallest implementation plan from an already measured AS-IS.
- `IMPLEMENT` — make a previously justified change and prove it.
- `VERIFY` — attack or independently validate an implementation.

Do not silently combine all four into one giant mission.

For architectural uncertainty, default to:

`DIAGNOSE → fresh IMPLEMENT mission → VERIFY`

Use Git and repository artifacts for continuity between missions, not conversational memory.

## 2. Build a Mission Card internally

Before opening many files, reduce the request to this compact structure:

```text
OBJECTIVE      one concrete outcome
SCOPE          exact components / paths / cards / boundary
MODE           DIAGNOSE | PLAN | IMPLEMENT | VERIFY
BASE           branch + measured HEAD
AUTHORITIES    only canonical files / law IDs needed
EVIDENCE       what must be measured
DONE           3–7 objective completion conditions
NON-GOALS      3–7 explicit exclusions
```

If this cannot fit on roughly one screen, the mission is probably too broad.
Split it before implementation.

Do not turn the Mission Card into a large new document unless the user explicitly asks for one.

## 3. Repository authority beats prompt repetition

Never paste or restate large canonical laws into the task when a stable owner already exists.

Instead:

1. identify the canonical owner;
2. read the exact relevant section(s);
3. record the law IDs / paths used;
4. test whether runtime actually conforms.

Examples in this repository:

- Collection law → `BIBLIA-CANONICA-DA-COLETA.md`, targeted `COL-LAW-*` sections.
- System Map law → `AGENTS.md`, targeted relevant section only after satisfying the repository instruction to read it.
- permanent project instructions → `CLAUDE.md`.
- evidence method → `README.md`.

`LAW_STATUS = CANONICAL` does not imply `IMPLEMENTATION = CORRECT`.
Always measure implementation separately.

## 4. Read progressively, not exhaustively

Start with the smallest context able to answer the current question.

Preferred order:

```text
mission target
→ its owner
→ direct callers / consumers
→ exact canonical law sections
→ tests / proofs
→ only then wider repository search
```

Do not preload entire large files merely because they are important.
Use search/find to locate relevant sections and expand only when necessary.

Do not read the whole Bible to audit three cards when five law sections decide those cards.

## 5. One mission, one primary question

A mission should answer one main question.

Good:

> Do the three control-plane cards represent the real runtime and the canonical Collection laws?

Bad:

> Audit the three cards, fix RAW→READY, redesign the map, integrate Stories, harden Security, run ten red teams, deploy, and document everything.

If independent work is discovered, register a handoff and keep the current mission focused.

## 6. Architecture: diagnose before changing

For architecture, topology, ownership, or plumbing work:

1. measure AS-IS;
2. distinguish runtime from map/documentation;
3. identify the canonical law;
4. classify mismatch;
5. edit only after the mismatch is proved.

Never make the map look like the desired architecture before runtime has that architecture.

Remember:

```text
MAP != ARCHITECTURE
IMPORT != RUNTIME FLOW
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS
DECLARED != OBSERVED
TEST PATH != PRODUCTION PATH unless proved
```

## 7. For System Map/card audits, use a fixed compact schema

For each selected card:

```text
ROLE
PURPOSE
OWNER
RUNTIME PRODUCERS
RUNTIME CONSUMERS
INPUT
OUTPUT
STATUS
LAW
VERDICT
```

For each immediate edge:

```text
FROM → TO
TYPE = DATA | CONTROL | POLICY | CONFIG | RULE | READ | WRITE | PROOF | CODE | META
RUNTIME = YES | NO | UNKNOWN
EVIDENCE
VERDICT
```

Audit only the requested cards plus immediate neighbors unless evidence forces expansion.

Do not use generic `RECEBE DE / ENVIA PARA` as semantic proof.

## 8. Keep diagnosis and implementation separate when uncertainty is material

If the current architecture is not yet known, do not edit while discovering it.

A good diagnostic mission ends with:

- AS-IS;
- exact violations / gaps;
- evidence;
- smallest implementation target.

Then start implementation from a fresh session/context when practical.

Do not carry a giant research transcript into implementation if Git/artifacts can preserve the result more compactly.

## 9. Subagents are bounded probes, not a meeting

Use subagents only when the questions are genuinely independent.

Each subagent must receive:

```text
ONE QUESTION
READ-ONLY unless explicitly needed
LIMITED PATHS / SOURCES
SHORT RETURN FORMAT
```

Prefer 2–4 focused probes over 8–10 broad agents.

Do not ask every subagent to read the whole repo.
Do not let multiple agents return long overlapping essays into the main context.

Main-session context is a scarce resource.

## 10. “Work all night” means a queue of checkpoints, not a 200-item prompt

For long autonomous work, define 3–6 checkpoints with dependency order.

Example:

```text
CP1 measure
CP2 implement smallest proven fix
CP3 verify production path
CP4 adversarial test
CP5 regenerate derived artifacts
CP6 final freeze
```

At each checkpoint:

- commit only coherent work;
- push stable checkpoints when appropriate;
- continue automatically if the next step does not require a human decision.

Do not invent extra work merely to consume time.

If blocked on one branch of work, continue independent checkpoints.

## 11. Use Git as external memory

For long or multi-session tasks, persist state in:

- branch / worktree;
- semantic commits;
- existing canonical machine-readable artifacts;
- one small handoff only when necessary.

Do not rely on keeping a very long conversation alive.

Before resuming after interruption:

```text
git fetch --all --prune
measure branch + HEAD + worktree
read delta since checkpoint
continue from evidence
```

Never inherit a remembered HEAD as truth.

## 12. Completion criteria must be few and executable

Define `DONE` using 3–7 checks that directly prove the objective.

Prefer:

```text
3/3 selected cards audited
100% immediate edges classified
runtime caller of Collection Request known
executor-selection authority known
unexplained immediate edges = 0
new failures = 0
```

Avoid dozens of delivery fields that do not affect the decision.

A checklist is useful only if every item can change the verdict.

## 13. PASS is about the mission, not the whole project

A narrow mission may pass while the larger system remains partial.

State both when useful:

```text
MISSION = PASS
SYSTEM / FOUNDATION = PARTIAL
```

Do not widen the mission at the end just because neighboring debt exists.

Do not call `PASS` when the central completion condition was replaced by a proxy.

## 14. Separate evidence levels

Do not treat these as equivalent:

```text
DECLARED
WIRED
EXECUTABLE
OBSERVED
PROVEN_END_TO_END
```

Examples:

- module imported → usually `WIRED`;
- workflow calls script → at most `EXECUTABLE` without further proof;
- runtime produced the expected artifact through the canonical path → candidate for `OBSERVED/PROVEN_END_TO_END`.

Use the repository's canonical evidence states where they already own the terminology.

## 15. Red team after the happy path, and only against the central invariant

Do not create a huge generic red-team section before implementation.

First prove the intended path.
Then attack the 2–5 assumptions most capable of creating a false green.

Good mutation tests answer questions like:

- Can a button bypass the canonical request?
- Can CODE be misdrawn as DATA?
- Can a test producer be counted as production?
- Can missing evidence become ZERO?

Every adversarial test must be tied to a named invariant.

## 16. Deterministic requirements belong in gates/hooks, not repeated prose

If a rule must never be forgotten and can be tested mechanically, prefer an executable guard rather than repeating it in every mission.

Examples:

- generated System Map must validate;
- no generated drift;
- no new unauthorized bypass;
- no new public secret exposure.

Do not create a new gate unless there is a proven regression class and a single clear owner.

## 17. Avoid expanding the repository with mission bureaucracy

Before creating a document, registry, script, or owner, ask:

```text
Does an owner already exist?
Can this be a test against the existing owner?
Is this artifact evidence, or would it become a second truth?
```

Prefer editing the canonical owner or creating an executable proof over adding another report.

Delete experiment-only code before finalizing unless it has an ongoing operational role.

## 18. When the user is inspecting cards manually

If the user sends specific System Map cards/screenshots:

- analyze the selected card only;
- inspect its real owner/callers when tools are available;
- accumulate findings conceptually;
- do not immediately generate a giant repair mission after each card;
- after a coherent group is understood, implement the group together.

This prevents local fixes from creating a Frankenstein architecture.

## 19. Reporting format

Keep the final engineering report decision-oriented.

Default:

```text
VERDICT

WHAT WAS MEASURED
WHAT CHANGED
WHAT THE PROOF SAYS
WHAT REMAINS OUTSIDE THIS MISSION

GIT
branch · initial head · final head · pushed

Em palavras fáceis
2–6 short answers
```

Do not reproduce the entire task specification in the delivery.

## 20. Stop rules

Stop and ask for a human decision only when the next action requires one of:

- choosing between two legitimate authorities with insufficient evidence;
- destructive or production mutation not already authorized;
- new product/semantic policy;
- credential/admin action unavailable to the agent;
- legal/business decision.

Do not stop for:

- an unrelated inherited failure;
- one UNKNOWN when other independent work remains;
- a parallel branch advancing;
- a test that can be reproduced locally;
- lack of conversational history that Git/repo state can resolve.

## 21. Mission quality self-check

Before starting substantial work, verify:

```text
[ ] one primary objective
[ ] one primary mode
[ ] narrow scope
[ ] measured base
[ ] targeted authorities, not whole-library reading
[ ] 3–7 completion checks
[ ] explicit non-goals
[ ] no repeated canonical law text
[ ] no unnecessary subagent fan-out
[ ] no implementation before AS-IS when architecture is uncertain
```

If several boxes fail, rewrite the mission internally before executing.

# Final principle

The repository should carry the knowledge.
The mission should carry the intent.
The tests should carry the proof.
Git should carry the continuity.

Do not make the prompt carry all four.