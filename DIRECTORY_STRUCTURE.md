# Directory Structure - Complete Project Map

```
e:\TEST\
│
├── 📄 Documentation (14 files)
│   ├── START_HERE.md                 ⭐ Start here first!
│   ├── QUICKSTART.md                 Quick setup guide
│   ├── README.md                     Project overview
│   ├── FINAL_SUMMARY.md              Phase 1 summary
│   ├── COMPLETION_REPORT.md          What was built
│   ├── STATUS.md                     Current status
│   ├── EXECUTION_SUMMARY.md          Implementation details
│   ├── PROJECT_STRUCTURE.md          Code organization
│   ├── DOCUMENTATION_INDEX.md        Doc index
│   ├── CONTRIBUTING.md               Developer guide
│   ├── QUICKSTART.md                 Setup instructions
│   ├── tasks.md                      250+ task tracking
│   ├── progress.md                   Progress metrics
│   └── PHASE2_PLAN.md                Next phase plan
│
├── 📂 apps/                          Frontend Applications
│   └── web/                          Next.js Frontend
│       ├── 📂 app/                   Next.js App Router
│       │   ├── layout.tsx            Root layout
│       │   ├── page.tsx              Home page
│       │   ├── globals.css           Global styles
│       │   ├── providers.tsx         Theme & Query providers
│       │   ├── 📂 auth/              Authentication
│       │   │   ├── 📂 login/
│       │   │   │   └── page.tsx      Login page
│       │   │   └── 📂 register/
│       │   │       └── page.tsx      Register page
│       │   └── 📂 dashboard/         User Dashboard
│       │       └── page.tsx          Dashboard page
│       ├── 📂 lib/                   Utilities
│       │   └── api-client.ts         Axios HTTP client
│       ├── 📂 public/                Static assets
│       ├── 📂 components/            (To be added in Phase 2)
│       ├── 📂 hooks/                 (To be added in Phase 2)
│       ├── 📂 __tests__/             Test files
│       ├── package.json              Dependencies
│       ├── tsconfig.json             TypeScript config
│       ├── next.config.js            Next.js config
│       ├── tailwind.config.js        Tailwind config
│       ├── postcss.config.js         PostCSS config
│       ├── .eslintrc.json            ESLint config
│       ├── jest.config.js            Jest config
│       └── .env.example              Environment template
│
├── 📂 services/                      Backend Services
│   ├── api/                          FastAPI Backend
│   │   ├── 📂 routes/                API Endpoints
│   │   │   ├── auth.py               Authentication routes
│   │   │   ├── users.py              User management routes
│   │   │   ├── exams.py              Exam routes
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 utils/                 Utilities
│   │   │   ├── auth.py               JWT & password utils
│   │   │   └── __init__.py
│   │   │
│   │   ├── 📂 migrations/            Database Migrations
│   │   │   ├── env.py                Alembic config
│   │   │   ├── script.py.mako        Migration template
│   │   │   ├── 📂 versions/
│   │   │   │   └── 001_create_users_tables.py
│   │   │   └── alembic.ini
│   │   │
│   │   ├── 📂 tests/                 Test Suite
│   │   │   ├── conftest.py           Test fixtures
│   │   │   ├── test_auth.py          Auth tests
│   │   │   └── __init__.py
│   │   │
│   │   ├── main.py                   FastAPI app factory
│   │   ├── config.py                 Configuration
│   │   ├── database.py               Database setup
│   │   ├── models.py                 SQLAlchemy models
│   │   ├── schemas.py                Pydantic schemas
│   │   ├── Dockerfile                API container
│   │   ├── __init__.py
│   │   └── .env.example              Environment template
│   │
│   ├── ai/                           AI Services (Phase 3+)
│   │   ├── 📂 tutor/                 (To be added)
│   │   ├── 📂 evaluation/            (To be added)
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 📂 packages/                      Shared Code
│   ├── shared/                       Shared utilities
│   │   ├── 📂 types/                 (To be added)
│   │   ├── 📂 constants/             (To be added)
│   │   └── __init__.py
│   └── ui-components/               (To be added)
│
├── 📂 docs/                          Documentation
│   ├── prd.md                        Product requirements
│   ├── implementation.md             Implementation plan
│   ├── architecture.md               (To be added)
│   ├── api-spec.md                   (To be added)
│   └── deployment.md                 (To be added)
│
├── 📂 scripts/                       Utility Scripts
│   ├── seed-db.py                    (To be added)
│   ├── backup-db.sh                  (To be added)
│   └── deploy.sh                     (To be added)
│
├── 📂 .github/                       GitHub Configuration
│   └── 📂 workflows/
│       └── ci-cd.yml                 CI/CD Pipeline
│
├── 📦 Configuration Files (Root)
│   ├── .env.example                  Environment template
│   ├── .gitignore                    Git ignore rules
│   ├── .prettierrc                   Prettier config
│   ├── docker-compose.yml            Local dev services
│   ├── docker-compose.prod.yml       (To be added)
│   ├── package.json                  Root workspace config
│   ├── pyproject.toml                Python project config
│   ├── requirements.txt               Python dependencies
│   ├── tsconfig.json                 (Shared TS config)
│   ├── .gitattributes                (Optional)
│   └── Makefile                      (To be added)
│
└── 📊 Project Files
    ├── .git/                         Git repository
    ├── node_modules/                 (Generated)
    ├── venv/                         (Generated, optional)
    └── .venv/                        (Generated, optional)
```

---

## 📂 Important Directories

### Frontend (`apps/web/`)
- **app/** - Next.js pages (route handlers)
- **lib/** - Utilities (API client, helpers)
- **public/** - Static assets
- **components/** - (To be added in Phase 2)
- **hooks/** - (To be added in Phase 2)
- **__tests__/** - Test files

### Backend (`services/api/`)
- **routes/** - API endpoints (auth, users, exams)
- **utils/** - Utilities (JWT, password)
- **models.py** - SQLAlchemy ORM models
- **schemas.py** - Pydantic validation
- **database.py** - Connection & session
- **config.py** - Configuration
- **main.py** - FastAPI app
- **migrations/** - Database migrations

### Documentation (`docs/` + root)
- **prd.md** - Product requirements
- **implementation.md** - Implementation plan
- **README.md** - Project overview
- **QUICKSTART.md** - Setup guide
- **CONTRIBUTING.md** - Developer guide

### Configuration (root)
- **docker-compose.yml** - Local services
- **package.json** - Frontend + workspace
- **pyproject.toml** - Python config
- **requirements.txt** - Python dependencies
- **.env.example** - Environment template

---

## 🗂️ What Each Directory Contains

| Directory | Purpose | Status |
|-----------|---------|--------|
| `apps/web/app/` | Page components | ✅ 4 pages |
| `services/api/routes/` | API endpoints | ✅ 8 routes |
| `services/api/models.py` | Database models | ✅ 4 models |
| `services/api/migrations/` | DB migrations | ✅ Created |
| `services/api/tests/` | Unit tests | ✅ 5+ tests |
| `docs/` | Design docs | ✅ 2 docs |
| `.github/workflows/` | CI/CD pipeline | ✅ Configured |
| `packages/shared/` | Shared code | ⏳ Placeholder |
| `services/ai/` | AI services | ⏳ Placeholder |

---

## 📄 File Types in Project

### Python Files (15+)
- `*.py` - Source code
- `models.py` - ORM models
- `schemas.py` - Validation
- `config.py` - Configuration
- `main.py` - App entry point

### TypeScript Files (8+)
- `*.tsx` - React components
- `*.ts` - Utilities
- `tsconfig.json` - Config

### Configuration (25+)
- `*.json` - JSON configs
- `*.yml` - YAML configs
- `*.toml` - TOML configs
- `Dockerfile` - Container config
- `docker-compose.yml` - Services
- `.env.example` - Env template

### Documentation (15+)
- `*.md` - Markdown docs
- `README.md` - Overview
- `QUICKSTART.md` - Guide
- `CONTRIBUTING.md` - Dev guide

### Database (2+)
- `alembic.ini` - Migration config
- `001_*.py` - Migration scripts

---

## 🔄 File Relationships

### Authentication Flow
```
pages/auth/login/ ──→ lib/api-client.ts ──→ routes/auth.py ──→ utils/auth.py
```

### User Dashboard
```
pages/dashboard/ ──→ lib/api-client.ts ──→ routes/users.py ──→ models.py
```

### Database Schema
```
models.py ──→ schemas.py ──→ migrations/001_*.py ──→ PostgreSQL
```

### Configuration
```
.env.example ──→ config.py ──→ main.py ──→ routes/
```

---

## 📊 File Count by Type

| Type | Count |
|------|-------|
| Python files | 15+ |
| TypeScript files | 8+ |
| Configuration files | 25+ |
| Documentation files | 15 |
| Test files | 2 |
| Migration files | 2 |
| CSS files | 1 |
| **Total** | **70+** |

---

## 🚀 Quick Navigation

### To Run the App
```
docker-compose.yml → See START_HERE.md
```

### To Understand Code
```
Project → README.md → PROJECT_STRUCTURE.md → Source files
```

### To Add Features
```
PHASE2_PLAN.md → CONTRIBUTING.md → Source files
```

### To Deploy
```
docker-compose.prod.yml → .github/workflows/ci-cd.yml
```

---

## 🔑 Key Files You'll Use

### Every Day
- `docker-compose.yml` - Start services
- `services/api/main.py` - Backend entry
- `apps/web/app/page.tsx` - Frontend entry
- `.env.example` - Configuration

### When Developing
- `services/api/routes/` - API endpoints
- `apps/web/app/` - Pages
- `services/api/models.py` - Database
- `CONTRIBUTING.md` - Guidelines

### When Deploying
- `docker-compose.prod.yml` - Production
- `.github/workflows/ci-cd.yml` - CI/CD
- `Dockerfile` - Container image
- `requirements.txt` - Dependencies

### When Documenting
- `README.md` - Overview
- `docs/prd.md` - Requirements
- `CONTRIBUTING.md` - Guidelines
- `QUICKSTART.md` - Setup

---

## 💡 Tips for Navigation

### To find a file
1. Check PROJECT_STRUCTURE.md
2. Search for filename: `find . -name "filename"`
3. Use VS Code Find (Ctrl+P)

### To understand flow
1. Start with route file
2. Check models.py
3. Review schemas.py
4. See database.py

### To add a feature
1. Read PHASE2_PLAN.md
2. Check CONTRIBUTING.md
3. Copy similar pattern
4. Test with docker

---

**Use this map to navigate the project!**

Start with [START_HERE.md](START_HERE.md) or your chosen file above.
