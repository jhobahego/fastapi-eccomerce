---
type: constitution
title: FastAPI Ecommerce Backend — Constitution
description: The non-negotiable principles every rsc-sdd phase obeys for this project.
tags: [sdd, constitution, fastapi, ecommerce]
timestamp: 2026-09-22T17:00:00Z
topic: sdd
version: v1.0.0
---

# FastAPI Ecommerce Backend — Constitution

> Version: v1.0.0 · Ratified: 2026-09-22 · Last amended: 2026-09-22
> The non-negotiable principles every rsc-sdd phase obeys. Stack mechanics live in the project docs and config; this file ratifies the principle and links the detail.

## 1. Stack canon

1. Primary language and runtime: Python 3.11+ with FastAPI, SQLAlchemy, Pydantic, and PostgreSQL. Detail: `app/`, `pyproject.toml`, and `requirements.txt`.
2. Frameworks are fixed: FastAPI for the API layer, SQLAlchemy for persistence, Pydantic for validation, and PostgreSQL for the primary database. Changing a core framework is a MAJOR amendment.
3. Package installation uses the repository-managed Python environment and lock or requirements files committed to the repo. One environment contract is maintained per deployment target.

## 2. Quality bar

4. Code is formatted, lint-clean, and reviewable before merge. The project uses pytest as the working quality gate and keeps the test suite green for the changed scope.
5. Database schema changes require an Alembic migration and a verification step before merge. No schema change ships without migration evidence.
6. Tests gate the merge: TDD-style red → green → edge-case verification → refactor for changed behavior. The project keeps the existing pytest test suite as the default check.

## 3. Conventions

7. Naming and structure follow the current domain layout: API endpoints under `app/api`, models under `app/models`, schemas under `app/schemas`, repositories under `app/repositories`, and services under `app/services`.
8. API errors and response contracts are explicit and consistent: validation errors and auth failures must be handled predictably, and business errors are surfaced in a clear, stable shape.
9. Commit messages are human-authored and descriptive. AI assistance does not appear in the git authorship or commit footer.

## 4. Branching & shipping

10. Work happens on a branch off `main`; merge via PR. Direct pushes to the default branch are not allowed for feature work.
11. Git authorship is the human's. No `Co-Authored-By` lines, no AI-generated footer, and no claim that the human is the AI.

## 5. Security & privacy floor

12. No secret is ever committed. Secrets load from environment variables, `.env` files that are ignored by git, or project-managed deployment config.
13. Authentication and authorization are enforced by the JWT and role validation flow in the app. Endpoints with protected business logic require explicit auth checks and must not bypass the project security contract.

## 8. Knowledge & decisions

16. Every significant decision is appended to `02-DOCS/wiki/sdd/decisions.md` with date, options considered, and the reason for the choice. The constitution is the highest-order decision record for the project.

## Definition of Done (the merge bar `verify` runs against)

A change ships only when ALL hold:

- [ ] Tests pass for the changed scope and the existing pytest suite remains green.
- [ ] Schema changes include the Alembic migration path and validation evidence.
- [ ] Conventions and module boundaries are followed.
- [ ] No secrets or credentials are committed.
- [ ] Branch and authorship rules are obeyed.
- [ ] Significant decisions are recorded in `02-DOCS/wiki/sdd/decisions.md`.

## Amendment log (append-only)

| Date | Version | Change | Why |
|------|---------|--------|-----|
| 2026-09-22 | v1.0.0 | Ratified initial constitution. | Project kickoff and rsc harness activation. |
