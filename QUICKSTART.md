# 🚀 Quick Start Guide

Get the Intelligent Test Prep Platform running in 5 minutes.

---

## Prerequisites

- Docker & Docker Compose (recommended for simplicity)
- OR: Node.js 18+, Python 3.11+, PostgreSQL 15+
- Git

---

## Option 1: Docker Compose (Recommended)

### Step 1: Clone & Setup
```bash
cd e:\TEST
cp .env.example .env.local
```

### Step 2: Start Services
```bash
docker-compose up -d
```

Services will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- FastAPI (port 8000)
- Next.js (port 3000)

### Step 3: Access Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 4: Test Account
```
Email: test@example.com
Password: TestPassword123!
```

Register a new account instead.

---

## Option 2: Manual Setup

### Backend Setup

```bash
# Navigate to API directory
cd services\api

# Create virtual environment
python -m venv venv
source venv\Scripts\activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../../requirements.txt

# Set environment variables
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd apps\web

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

## First Steps

### 1. Register Account
1. Visit http://localhost:3000
2. Click "Register"
3. Enter email and password
4. Submit form
5. Redirected to dashboard

### 2. View Dashboard
- Profile information displayed
- Quick action cards available
- Select exams to get started

### 3. Explore API
- Visit http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly

---

## Project Structure

```
e:\TEST\
├── apps/web/              # Next.js frontend
├── services/
│   ├── api/               # FastAPI backend
│   └── ai/                # AI services (Phase 3+)
├── packages/shared/       # Shared utilities
├── docs/                  # Documentation
├── docker-compose.yml     # Local dev environment
├── package.json           # Frontend dependencies
├── pyproject.toml         # Python config
└── requirements.txt       # Python dependencies
```

---

## Common Commands

### Backend
```bash
# Start server
uvicorn services.api.main:app --reload

# Run tests
pytest services/api/tests/

# Format code
black services/

# Type check
mypy services/

# Lint
flake8 services/
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint and format
npm run lint
npm run format
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild images
docker-compose up -d --build
```

---

## Testing

### Run Backend Tests
```bash
pytest services/api/tests/
```

### Run Frontend Tests
```bash
cd apps/web
npm run test
```

### Run All Tests
```bash
npm run test  # From root
```

---

## Database

### Access PostgreSQL
```bash
# With Docker
docker-compose exec postgres psql -U testprep -d testprep_db

# Direct (if installed locally)
psql -U testprep -d testprep_db
```

### View Migrations
```bash
cd services/api
alembic current
alembic history
```

### Create New Migration
```bash
cd services/api
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## Environment Variables

Key variables in `.env.local`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=http://localhost:3000

# API
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### "Connection refused" error
- Ensure Docker is running
- Check port availability: `netstat -an | findstr :5432`
- Verify `.env.local` database URL

### "Port already in use"
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Database migration failed
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Module not found error
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
npm install --force
```

### CORS errors in browser
- Verify `CORS_ORIGINS` in `.env.local`
- Check that API and frontend URLs match
- Clear browser cache

---

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-01-08T10:30:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

### View Logs
```bash
# Docker compose
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f web
```

---

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/exam-selection
```

### 2. Make Changes
```bash
# Edit files in editor
# Backend: services/api/**/*.py
# Frontend: apps/web/**/*.tsx
```

### 3. Test Changes
```bash
pytest services/api/tests/
npm run test --workspace=web
```

### 4. Format Code
```bash
npm run format  # Prettier
black services/
```

### 5. Commit
```bash
git add .
git commit -m "feat: add exam selection"
```

### 6. Push & Create PR
```bash
git push origin feature/exam-selection
```

---

## Deployment

### Build Docker Image
```bash
docker build -t test-prep:latest .
```

### Push to Registry
```bash
docker tag test-prep:latest your-registry/test-prep:latest
docker push your-registry/test-prep:latest
```

### Deploy to Azure/AWS
- See `docs/deployment.md` (in future)

---

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **README**: [README.md](README.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Product Spec**: [docs/prd.md](docs/prd.md)
- **Implementation Plan**: [docs/implementation.md](docs/implementation.md)
- **Tasks**: [tasks.md](tasks.md)
- **Progress**: [progress.md](progress.md)

---

## Next Steps

### After Getting Started
1. ✅ Register and explore dashboard
2. ✅ View API documentation
3. ✅ Run tests
4. 📖 Read [CONTRIBUTING.md](CONTRIBUTING.md)
5. 🚀 Start Phase 2: Core Learning

### Phase 2 Tasks
- Build question bank
- Implement reading module
- Add listening practice
- Create vocabulary builder
- Implement grammar exercises

See [PHASE2_PLAN.md](PHASE2_PLAN.md) for details.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start services |
| `docker-compose down` | Stop services |
| `npm run dev` | Frontend dev server |
| `npm run build` | Build frontend |
| `pytest` | Run tests |
| `npm run lint` | Lint code |
| `npm run format` | Format code |

---

## Performance Tips

1. **Development**: Use `--reload` flag for auto-restart
2. **Production**: Disable debug mode in `.env`
3. **Database**: Add indexes for frequently queried columns
4. **Caching**: Use Redis for session data
5. **Images**: Compress before upload

---

## Security Checklist

- [ ] Change JWT_SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Update CORS_ORIGINS for production domain
- [ ] Use environment variables for secrets
- [ ] Enable database SSL connections
- [ ] Set up rate limiting
- [ ] Configure CSP headers
- [ ] Use strong passwords
- [ ] Enable 2FA (optional)

---

**Ready to go!** 🎉

Start developing at http://localhost:3000

For detailed documentation, see the docs folder or visit the API docs at http://localhost:8000/docs
