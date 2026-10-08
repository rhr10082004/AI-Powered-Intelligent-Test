# Progress Tracker

## Current Status (2026-10-07)
- **Project**: AI-Powered Intelligent Test Preparation Platform
- **Status**: Local MVP flows work; production deployment configuration is prepared.
- **Completion percentage**: Not estimated. The percentages below in the historic checklist were based on an earlier snapshot and are superseded.
- **Live hosting**: Not deployed. Vercel CLI/project link is unavailable in this workspace; Render and Vercel account linking is still required.

## Phase Completion

### Phase 1: Foundation
- Status: Core auth, account, exam enrollment, and Next.js foundation implemented.
- Implemented: email verification and password reset requests with hashed, expiring, single-use tokens; SMTP delivery hooks; and frontend verification/recovery screens. Per-account resend requests are throttled.
- Remaining: configure and verify production SMTP, gate protected features on verified email, add login/API rate limiting, durable refresh/logout revocation, production audit events, and broader end-to-end tests.

### Completed Tasks in Phase 1:
- [x] Initialize Git repository with .gitignore
- [x] Create root package.json with workspaces configuration
- [x] Create root pyproject.toml and requirements.txt for backend
- [x] Create Docker and docker-compose configuration
- [x] Set up environment configuration (.env.example files)
- [x] Create shared constants and types across monorepo
- [x] Create CI/CD pipeline (GitHub Actions)
- [x] Create contribution guidelines (CONTRIBUTING.md)
- [x] Create README.md with project overview
- [x] Setup database configuration and SQLAlchemy models
- [x] Create User, UserSettings, UserExam, AuditLog models
- [x] Create Pydantic schemas for validation
- [x] Implement JWT authentication utilities
- [x] Create FastAPI application structure
- [x] Implement user registration endpoint
- [x] Implement user login endpoint
- [x] Implement token refresh mechanism
- [x] Initialize Next.js frontend project
- [x] Setup Tailwind CSS and shadcn/ui
- [x] Create frontend API client with axios
- [x] Create home page
- [x] Create login page (frontend)
- [x] Create registration page (frontend)
- [x] Create dashboard page (frontend)
- [x] Setup database migrations with Alembic
- [x] Create User, UserSettings, UserExam, AuditLog SQL tables
- [x] Setup database connection pooling
- [x] Implement user profile GET/PUT endpoints
- [x] Implement exam enrollment endpoints (CRUD)
- [x] Add user routes to FastAPI app
- [x] Add exam routes to FastAPI app
- [x] Create authentication unit tests
- [x] Setup test fixtures and conftest
- [x] Setup Next.js project configuration (tsconfig, eslint, prettier)
- [x] Setup Tailwind CSS configuration
- [x] Create global CSS with design system variables
- [x] Create layout components (RootLayout)
- [x] Setup providers (Theme, Query Client)
- [x] Create API client with axios interceptors
- [x] Implement token refresh logic in API client
- [x] Create frontend authentication flow
- [x] Setup protected routes logic
- [x] Create user dashboard with profile display
- [x] Create quick action buttons on dashboard
- [x] Add logout functionality

### Phase 2: Core Learning
- Status: Usable local MVP implemented and smoke-tested.
- Implemented: a local practice bank of 100 reading passages (with two linked questions each), 100 listening transcripts/tracks (with two linked questions each), 150 vocabulary entries, and 100 grammar exercises; 100 selectable writing prompts per exam and 100 tutor starter prompts. The reading/listening scenarios are deterministic practice samples and the listening UI speaks their transcripts with browser speech synthesis. Also implemented answer-key-safe question APIs, grading with ownership checks, five-question reading diagnostics for IELTS/GRE/TOEFL, private grammar-attempt history, per-exam/section accuracy and streaks, track-question relationships, vocabulary review scheduling, idempotent study-session history, and dashboard summaries.
- Remaining: larger content import/pagination, consistent grammar roll-up into section analytics, and browser end-to-end coverage across learning flows.

### Phase 3: AI Services
- Status: Partial.
- Implemented: optional OpenAI tutor responses, lexical retrieval from course passages/vocabulary/grammar, a local topic-aware fallback, and private persistent tutor conversations with user-scoped history.
- Implemented: IELTS/TOEFL/GRE writing practice with optional OpenAI rubric feedback, local fallback feedback, criterion scores, and private saved submission history.
- Implemented: browser speech-to-text/typed transcript practice with a 100-prompt bank, local transcript rubric feedback and private response history.
- Remaining: vector ingestion/retrieval, OCR, provider rate limits/usage tracking, and recorded-audio pronunciation assessment.

### Phase 4: Adaptive Learning
- Status: Foundation only.
- Implemented: rule-based next-practice recommendation based on weakest saved section and proficiency-based vocabulary review intervals.
- Implemented: per-day, per-exam saved 30-minute plans generated from the learner's weakest recorded section, with private task completion and a dashboard entry point.
- Remaining: reminders, adaptive mock tests, score prediction, topic trend analysis, and a calendar/scheduling flow.

### Phase 5: Analytics & Gamification
- Status: Foundation only.
- Implemented: derived practice milestones, accuracy summaries, daily streak counters, a seven-day dashboard accuracy chart, CSV export of recent saved sessions, and an append-only private activity ledger that awards points for answers, completed sessions, writing reviews and plan tasks. The dashboard shows each learner's current level.
- Remaining: durable achievement unlock records, broader long-range analytics and exports, and notification delivery/preferences.

### Phase 6: Optimization & Launch
- Status: Deployment path prepared; launch remains blocked on external accounts and production verification.
- Implemented: Vercel monorepo settings, Render/PostgreSQL blueprint, production secret/CORS validation, migration/seed commands, clean production build.
- Remaining: connect Vercel/Render accounts, configure real domains/secrets, execute migrations on managed PostgreSQL, run cloud smoke tests, monitoring/backups, and security/load review.

## Latest Verification
- Frontend TypeScript check and production build pass after the expanded content, dashboard refresh, filters, and speaking page (21 routes; build targets the local API).
- Local API returns 107 passages, 104 listening tracks, 150 vocabulary entries and 100 grammar exercises. Speaking history route is registered and API health is healthy.
- Backend test suite: the latest full run before bulk-content and speaking work had 15 passing tests, including activity-ledger privacy/points, diagnostic coverage, auth recovery, grammar history, daily plan idempotency, tutor/writing history and short-draft validation. It has not been rerun after those additions.
- Alembic revisions 003 through 009 create tutor, writing, grammar-attempt, auth-token, daily-plan, and activity-ledger tables in a focused SQLite migration check. Revision 010 adds speaking history but has not been migration-tested. The full chain cannot run on SQLite because Phase 1 defines PostgreSQL UUID types; production PostgreSQL migration remains unverified.
- Existing local API smoke checks cover registration, enrollment, answer ownership/grading, vocabulary reviews, tutor responses, progress, and admin write rejection.
- Public reading/listening/grammar payloads omit answer keys until submission.
- Live Vercel deployment and PostgreSQL migration execution have not been performed from this workspace.

## Notes
- PRD created at docs/prd.md
- Implementation plan at docs/implementation.md
- Task tracking at tasks.md



