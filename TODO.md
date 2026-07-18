# TODO - Phase 2 (Week 1 scope)

## Database (Week 1)
- [x] Extend `services/api/models.py` with Phase 2 enums/types needed for Week 1:

  - [x] `Question`, `Answer`, `UserAnswer`

  - [x] `Passage`

  - [x] Enums/types: `Difficulty`, `Section`, `QuestionType`

- [ ] Create Alembic migration(s) for the new Week 1 tables + indexes (once models are added).


## Backend (Week 1)
- [ ] Add Week 1 Pydantic schemas in `services/api/schemas.py`:
  - [ ] Question list/get filters & responses
  - [ ] Answer submission request/response
  - [ ] Passage list/get response
  - [ ] Reading completion + progress response
- [ ] Implement Week 1 routes:
  - [ ] `services/api/routes/questions.py` (GET list, GET one, POST answer, GET my answers)
  - [ ] `services/api/routes/passages.py` (GET passages, GET passage details w/ questions)
  - [ ] `services/api/routes/reading.py` (POST complete, GET progress)
- [ ] Register new routers in `services/api/main.py`.

## Frontend (Week 1)
- [ ] Add Next.js pages for Week 1:
  - [ ] `/practice` minimal practice landing (links)
  - [ ] `/practice/reading` reading practice UI (passage + MCQ selector + timer placeholder)
- [ ] Ensure API client calls match backend routes.

## Quality
- [ ] Add/extend backend tests for Week 1:
  - [ ] questions list/get + basic filtering
  - [ ] answer submission correctness
  - [ ] reading completion updates progress
- [ ] Run `pytest`.

