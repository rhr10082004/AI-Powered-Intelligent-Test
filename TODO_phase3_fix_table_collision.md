# Phase 3 - Fix table collision errors (tracking)

## Completed
- Identified that app uses isolated learning models (`services/api/models_phase2_isolated.py`) but deprecated `services/api/models_phase2.py` still existed and could be imported accidentally.
- Updated `services/api/models_phase2.py` to **fail fast** with an `ImportError` so it cannot reintroduce the `questions` table collision.

## Next
- Restart API and verify the previous SQLAlchemy collision error is gone.
- If migrations still fail, validate Alembic `env.py` targets only `BasePhase2` from `models_phase2_isolated` (already confirmed).
- Run `alembic upgrade head` to ensure schema is applied cleanly.

