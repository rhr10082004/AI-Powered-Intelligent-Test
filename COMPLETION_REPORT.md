# Current Completion Report

This report reflects the verified local workspace snapshot. Historical phase percentages and task counts have been removed because they no longer match the implementation.

## Current state

- The application has a responsive Next.js frontend, FastAPI API, SQLAlchemy models and Alembic migrations.
- Learning features include reading, listening, vocabulary and grammar practice, exam-specific reading diagnostics, private grammar-attempt history, progress summaries, recommendations, saved tutor conversations, writing feedback/history, persisted daily study plans, and a private activity/points ledger. The dashboard includes a seven-day accuracy chart, learner level and recent-session CSV export.
- The idempotent local content seed now adds six reading passages with comprehension questions, three listening transcripts with questions, twelve vocabulary examples, six grammar lessons, nine selectable writing prompts, and four tutor starter questions. Seeded content is labeled as fictional practice material, not official exam material.
- The expanded seed provides at least 100 reading passages, 100 listening tracks, 150 vocabulary entries and 100 grammar exercises (107 passages and 104 tracks in the current local database). Passages/tracks have at least two linked questions. The writing studio offers 100 selectable prompts for each of IELTS, TOEFL and GRE; speaking and the tutor each have 100 prompts. Listening samples use browser speech synthesis rather than recorded audio.
- The dashboard has been redesigned with a weekly activity chart, next-step recommendations, learner points, milestones, quick skill links and recent sessions. Practice list endpoints and frontend requests now accept/display the expanded bank.
- Speaking practice now has 100 prompts, browser speech-to-text with a typed-transcript fallback, transcript-only rubric feedback, private response history and activity points. It clearly explains that pronunciation and prosody are not assessed.
- Adaptive mock tests now create mixed reading/listening attempts, choose difficulty from recent answer history, grade complete submissions, and retain private attempt history with section/topic accuracy. Their output is explicitly practice accuracy; calibrated exam score estimates are not implemented.
- Authentication includes registration/login, email verification requests, password reset requests, and expiring single-use action tokens. SMTP is configurable; local development can display a test token.
- Optional OpenAI tutor and writing feedback have local fallback behavior.

## Latest verification

- Backend tests: the last full suite run passed 15 tests before the latest bulk-content, speaking and mock-test additions; it has not been rerun since those changes.
- Frontend TypeScript check: passing after the latest changes.
- Local API content check: 107 passages, 104 tracks, 150 words and 100 grammar exercises returned; speaking API route is present and local API health is healthy.
- Production Next.js build: passing; 22 routes prerendered with the local API URL configured, including `/practice/mock-test`.
- API smoke check: demo login, 10-question mock start, submission, scoring and history passed against the local SQLite database.
- Alembic revisions 003 to 009 have a focused SQLite table-creation check. Revisions 010 and 011 add speaking and mock-test history; those migrations and a production PostgreSQL migration have not been verified.

## Remaining work

The live checklist is [TODO.md](TODO.md), and implementation notes are in [progress.md](progress.md). Remaining work includes authentication rate limiting and revocation, broader content import and browser end-to-end coverage, vector retrieval, OCR/provider usage controls, calibrated exam score estimates, reminders and calendars, durable achievement records/notifications, and external production launch checks.

## External publishing and launch

This workspace has no `.git` metadata, Git CLI, or connected GitHub repository, so changes cannot be pushed from here. Production deployment also needs hosting credentials, real domains, configured secrets (including SMTP), and managed database access.
