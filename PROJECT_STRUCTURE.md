# Project Structure

```
intelligent-test-prep-platform/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                    # GitHub Actions CI/CD pipeline
├── apps/
│   └── web/                             # Next.js frontend application
│       ├── app/
│       │   ├── layout.tsx               # Root layout
│       │   ├── page.tsx                 # Home page
│       │   ├── globals.css              # Global styles
│       │   ├── providers.tsx            # Theme & Query client providers
│       │   ├── auth/
│       │   │   ├── login/page.tsx       # Login page
│       │   │   └── register/page.tsx    # Registration page
│       │   └── dashboard/
│       │       └── page.tsx             # User dashboard
│       ├── lib/
│       │   └── api-client.ts            # Axios API client with interceptors
│       ├── public/                      # Static assets
│       ├── package.json                 # Frontend dependencies
│       ├── tsconfig.json                # TypeScript config
│       ├── next.config.js               # Next.js config
│       ├── tailwind.config.js           # Tailwind config
│       ├── postcss.config.js            # PostCSS config
│       └── .eslintrc.json               # ESLint config
├── services/
│   ├── api/                             # FastAPI backend
│   │   ├── routes/
│   │   │   ├── auth.py                  # Authentication endpoints
│   │   │   ├── users.py                 # User profile endpoints
│   │   │   └── exams.py                 # Exam enrollment endpoints
│   │   ├── migrations/
│   │   │   ├── env.py                   # Alembic environment config
│   │   │   ├── script.py.mako           # Migration template
│   │   │   └── versions/
│   │   │       └── 001_create_users_tables.py
│   │   ├── tests/
│   │   │   ├── conftest.py              # Test fixtures
│   │   │   └── test_auth.py             # Auth unit tests
│   │   ├── utils/
│   │   │   ├── auth.py                  # JWT & password utilities
│   │   │   └── __init__.py
│   │   ├── main.py                      # FastAPI app factory
│   │   ├── config.py                    # Configuration management
│   │   ├── database.py                  # Database setup
│   │   ├── models.py                    # SQLAlchemy ORM models
│   │   ├── schemas.py                   # Pydantic schemas
│   │   ├── Dockerfile                   # API container image
│   │   └── __init__.py
│   ├── ai/                              # AI/ML services (placeholder)
│   │   └── __init__.py
│   └── __init__.py
├── packages/
│   └── shared/                          # Shared utilities
│       └── __init__.py
├── docs/
│   ├── prd.md                           # Product requirements document
│   └── implementation.md                # Implementation plan
├── scripts/                             # Utility scripts (placeholder)
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── .prettierrc                          # Prettier config
├── docker-compose.yml                   # Local development setup
├── docker-compose.prod.yml              # Production setup (placeholder)
├── package.json                         # Root workspace config
├── pyproject.toml                       # Python project config
├── requirements.txt                     # Python dependencies
├── README.md                            # Project overview
├── CONTRIBUTING.md                      # Contribution guidelines
├── EXECUTION_SUMMARY.md                 # Phase 1 summary
├── tasks.md                             # Task tracking (250+ tasks)
└── progress.md                          # Progress tracking

```

## Key Files by Purpose

### Authentication & Security
- `services/api/utils/auth.py` - JWT & password utilities
- `services/api/routes/auth.py` - Auth endpoints
- `apps/web/lib/api-client.ts` - API client with token management

### Database
- `services/api/database.py` - Connection & session management
- `services/api/models.py` - SQLAlchemy ORM models
- `services/api/schemas.py` - Pydantic validation schemas
- `services/api/migrations/versions/001_*.py` - Database migrations

### API Endpoints
- `services/api/routes/auth.py` - Register, login, token refresh
- `services/api/routes/users.py` - Profile management
- `services/api/routes/exams.py` - Exam enrollment
- `services/api/main.py` - FastAPI app factory

### Frontend Pages
- `apps/web/app/page.tsx` - Home page
- `apps/web/app/auth/login/page.tsx` - Login form
- `apps/web/app/auth/register/page.tsx` - Registration form
- `apps/web/app/dashboard/page.tsx` - User dashboard

### Configuration & Setup
- `docker-compose.yml` - Local dev environment (PostgreSQL, Redis, Qdrant)
- `.env.example` - Environment variables reference
- `package.json` - Frontend + workspace dependencies
- `pyproject.toml` - Python project configuration
- `requirements.txt` - Python package versions

### Documentation
- `docs/prd.md` - Complete product requirements
- `docs/implementation.md` - Implementation phases
- `tasks.md` - 250+ task tracking across 6 phases
- `progress.md` - Current progress metrics
- `EXECUTION_SUMMARY.md` - What was built in Phase 1

### CI/CD & Testing
- `.github/workflows/ci-cd.yml` - Automated testing & deployment
- `services/api/tests/conftest.py` - Test configuration
- `services/api/tests/test_auth.py` - Authentication tests

### Styling & Assets
- `apps/web/app/globals.css` - Global design tokens
- `apps/web/tailwind.config.js` - Tailwind configuration
- `apps/web/postcss.config.js` - PostCSS configuration
- `.prettierrc` - Code formatting rules

## Database Schema

### Users Table
- id (UUID, PK)
- email (String, Unique)
- hashed_password (String)
- first_name, last_name (String, Optional)
- avatar_url, bio (String, Optional)
- is_active, is_verified, is_deleted (Boolean)
- created_at, updated_at, deleted_at (Timestamp)

### User Exams Table
- id (UUID, PK)
- user_id (UUID, FK to Users)
- exam_type (Enum: IELTS, GRE, TOEFL)
- target_score (String, Optional)
- skill_level (String: beginner/intermediate/advanced)
- is_active (Boolean)
- created_at, updated_at (Timestamp)

### User Settings Table
- id (UUID, PK)
- user_id (UUID, FK to Users)
- theme, language (String)
- notifications_email, notifications_push, notifications_reminder (Boolean)
- created_at, updated_at (Timestamp)

### Audit Logs Table
- id (UUID, PK)
- user_id (UUID, FK to Users, Optional)
- action, entity_type (String)
- entity_id (UUID, Optional)
- description (Text, Optional)
- ip_address (String, Optional)
- created_at (Timestamp)

## Service Architecture

### Backend Layers
1. **Routes** - HTTP endpoints (auth.py, users.py, exams.py)
2. **Schemas** - Pydantic validation (request/response)
3. **Models** - SQLAlchemy ORM (database entities)
4. **Utils** - Business logic (auth utilities)
5. **Database** - Connection & migrations

### Frontend Structure
1. **Pages** - App Router pages (auth, dashboard)
2. **Components** - Reusable React components (in progress)
3. **Hooks** - Custom React hooks (in progress)
4. **Lib** - Utilities (api-client)
5. **Styles** - Global & component styles

## External Services (Ready to Integrate)

### Development Environment
- PostgreSQL 15+ - Primary database
- Redis 7+ - Caching layer
- Qdrant - Vector database for embeddings

### Production Services (Configured but Not Integrated)
- OpenAI API - LLM & embeddings
- Google Cloud Speech - Speech recognition
- Cloud Vision - OCR
- AWS S3 - File storage
- SendGrid - Email service

---

**Total Files**: 60+
**Lines of Code**: 3000+
**Test Coverage**: Started (5+ unit tests)
**Documentation**: Comprehensive (PRD, Implementation plan, API docs)

Ready for Phase 2: Core Learning Modules
