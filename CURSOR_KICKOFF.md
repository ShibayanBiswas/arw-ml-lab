# Cursor kickoff — paste the block below into a new Cursor Agent chat

```
You are building the ARW ML Lab in this folder. It is a design kit; no app code exists yet.

1. Read these files fully before doing anything: AGENTS.md, CURSOR_PROMPT.md (especially §00 and §000),
   docs/ARCHITECTURE.md (v2.2; §45 Prediction Studio and §46 Hardening win over older sections),
   docs/STRESS_TEST.md and docs/PROGRESS.md. Follow every rule in .cursor/rules/.
2. Model: use the strongest reasoning ("thinking") model in the picker at its highest effort, not Auto.
   Plan each phase in Plan mode first and write docs/plans/PHASE_<n>_PLAN.md; wait for my approval.
3. Work strictly phase by phase in the order in CURSOR_PROMPT.md §000 (18 phases, starting with Phase 0).
   Do one phase per turn. Do not start the next phase on your own.
4. For the current phase: build it fully, no stubs, mocks or placeholder numbers in shipped code;
   run every acceptance criterion and the self-verification checklist yourself in the terminal;
   fix until green. Never skip, delete or weaken a test, and never invent results.
5. When the phase is green: write docs/PHASE_<n>_REPORT.md with the real command output,
   update docs/PROGRESS.md, commit with "phase <n>: <summary>", then STOP and report to me:
   what was built, AC results, deviations, open TODOs and the plan for the next phase.
6. Ask me before anything outside this folder: creating the GitHub repo, pushing, connecting
   Vercel/Render/Supabase, paid plans, production secrets, deploys. Never ask me to paste keys in chat;
   NVIDIA_API_KEY goes only into the backend server env (/opt/arw-ml-lab/.env on the Contabo VPS)
  and my local .env, never Vercel.
7. If anything in the spec is unclear or contradictory, stop and ask instead of guessing.

Start now: read the files, then plan Phase 0.
```

**To continue after a phase report (one line):**

```
Continue: re-read docs/PROGRESS.md and the last phase report, then plan and build the next phase per CURSOR_PROMPT.md §000 and stop when it is green.
```
