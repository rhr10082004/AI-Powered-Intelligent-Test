# Project TODO — Current Remaining Work

This checklist follows the verified project status in `progress.md`. `tasks.md` remains the original full product backlog; its unchecked items are not a live measure of completion.

## Current UI pass
- [x] Replace the text-only landing screen with responsive product-focused content and clear routes.
- [x] Add subtle entrance and ambient motion with reduced-motion support.
- [x] Refresh login and registration layouts while preserving their existing API flows.
- [x] Replace unreadable dashboard quick-action labels.
- [x] Redesign the learner dashboard around weekly practice, clear next steps, section accuracy and recent sessions.
- [x] Run frontend type-check and production build (local build targets the local API URL).
- [ ] Review all routes in a browser at desktop and mobile widths (landing/auth checked at 390px; practice routes still need browser review).

## Phase 1 — Foundation
- [x] Add email verification and password reset links with expiring, one-use tokens and recovery screens.
- [ ] Configure SMTP and verify delivery in production.
- [ ] Add login/API rate limiting, durable logout/refresh revocation, and auth audit events (account-action resend throttling is implemented).
- [ ] Expand auth, error-handling and end-to-end coverage.
- [ ] Finish production accessibility and responsive review across profile, onboarding, exams and dashboard.

## Phase 2 — Core learning
- [x] Reading, listening, vocabulary and grammar practice foundations are implemented.
- [x] Safe answer grading, study history, progress summaries and recommendations are implemented.
- [x] Add a five-question reading baseline for IELTS, GRE and TOEFL.
- [x] Expand local sample learning content with six additional reading passages, three listening tracks, twelve vocabulary words, and six grammar lessons.
- [x] Add selectable practice essay prompts for IELTS, GRE and TOEFL, plus tutor starter questions.
- [ ] Expand content import and review pagination for larger question banks.
- [x] Persist private grammar attempts, show recent history, and test repeated answers/account isolation.
- [x] Seed at least 100 reading passages, 100 listening tracks, 150 vocabulary entries and 100 grammar exercises; add 100 writing prompts per exam and 100 tutor prompt examples.
- [x] Add API integration coverage for auth recovery, tutor/writing history, grammar attempts, study plans and diagnostics.
- [ ] Add broad browser end-to-end coverage for the learning flows.

## Phase 3 — AI services
- [x] Tutor responses have optional OpenAI support and a local fallback.
- [x] Persist private tutor conversations with user-scoped history and ordered turns.
- [ ] Add vector retrieval ingestion/indexing.
- [x] Build writing evaluation and private submission history, with AI and local rubric modes.
- [x] Build browser speech-to-text speaking practice, transcript feedback and private response history (feedback explicitly does not score pronunciation).
- [ ] Add OCR study capture, provider usage tracking and rate limits.

## Phase 4 — Adaptive learning
- [x] Basic recommendations and vocabulary review intervals are available.
- [x] Persist personalized daily study plans and task completion.
- [ ] Add reminder scheduling and delivery.
- [x] Build adaptive mixed-section mock tests with difficulty selection, section/topic accuracy and private attempt history; benchmark score estimates remain future work.
- [ ] Add revision calendar and scheduling flows.

## Phase 5 — Analytics and motivation
- [x] Accuracy summaries, milestones and streak counters are available.
- [x] Persist learner activity events and award points for completed practice actions.
- [x] Add a seven-day practice accuracy chart and CSV export on the dashboard.
- [x] Show learner levels from the durable points ledger.
- [ ] Persist achievement unlock records.
- [ ] Add notification delivery and preference controls.

## Phase 6 — Optimization and launch
- [x] Deployment configuration for Vercel, Render and PostgreSQL is prepared.
- [ ] Connect hosting accounts and configure production domains/secrets.
- [ ] Run migrations and smoke checks against managed production services.
- [ ] Complete monitoring, backups, security and load reviews.
- [ ] Confirm launch readiness and document post-launch ownership.

## Publishing
- [ ] Connect the GitHub integration; this workspace has no .git directory or Git CLI.
- [ ] Review the final diff, commit the approved changes and publish them to the repository.

## Current environment blockers
- Node.js and Python are installed outside PATH and can be invoked directly. Git is not installed, this workspace has no .git metadata, and GitHub is not connected, so publishing remains blocked. Visual checks have covered the landing/auth screens at mobile width; the new practice and writing screens still need browser review.
- Production deployment still requires access to the project’s hosting accounts and configured secrets.



