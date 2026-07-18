# Phase 3 scaffolding note

Current issue encountered when importing FastAPI app:
- SQLAlchemy InvalidRequestError: Table 'questions' is already defined for this MetaData instance.

Cause: both services/api/models_phase2.py (Phase 2) and at least one other module are defining a table named `questions` on the same SQLAlchemy Base/MetaData.

Next step:
- Find where `questions` table is defined twice.
- Fix by ensuring only one declarative model maps to the `questions` table.
  - Typical fix: remove duplicate model import/definition, or change the Base for phase2 models, or set `__table_args__ = {"extend_existing": True}` temporarily.

This file is a temporary tracker for the fix.
