# SDD decisions log

This file captures significant project decisions that affect scope, architecture, or delivery.

## 2026-09-22

- Decision: Keep the project-local rsc harness focused on the FastAPI backend and the SDD workflow, with minimal repo-specific skill selection.
- Why: The repo already has a clear backend scope, a Python stack, and a documented test workflow; broad tooling would add context without immediate value.
- Alternatives considered: full generic harness, monorepo scaffolding, broader deployment ops install.
- Result: Accept the project-local harness with SDD, project memory, and minimal skill selection.
