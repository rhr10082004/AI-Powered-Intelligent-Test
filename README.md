# AI-Powered Intelligent Test Preparation Platform

A comprehensive, modern, AI-assisted platform for preparing students for IELTS, GRE, and TOEFL exams.

**Live app:** [ai-powered-intelligent-test.vercel.app](https://ai-powered-intelligent-test.vercel.app/)  
**Source:** [GitHub repository](https://github.com/rhr10082004/AI-Powered-Intelligent-Test)

## 🌟 Features

- **Multi-Exam Support**: IELTS, GRE, TOEFL in one unified platform
- **AI Tutor**: 24/7 intelligent tutoring powered by GPT and RAG
- **Adaptive Learning**: Intelligent difficulty adjustment based on performance
- **Comprehensive Practice**:
  - Reading comprehension
  - Listening with real audio
  - Writing with AI essay evaluation
  - Speaking with pronunciation analysis
  - Vocabulary & grammar practice
- **Personalized Study Plans**: AI-generated custom learning paths
- **Real-time Feedback**: Instant evaluation on essays and speaking
- **Analytics Dashboard**: Track progress with detailed analytics
- **Gamification**: Streaks, badges, and achievement system
- **OCR Scanner**: Handwritten text recognition for answer sheets
- **Score Prediction**: ML-powered score forecasting

## 🏗️ Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **UI Library**: React + shadcn/ui
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query + Zustand
- **Forms**: React Hook Form + Zod

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Vector DB**: Qdrant
- **AI**: OpenAI GPT-4, Embeddings, Whisper

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes-ready
- **Storage**: S3-compatible (AWS S3, MinIO)

## 📋 Project Structure

```
.
├── apps/
│   └── web/                 # Next.js frontend application
│       ├── app/             # App Router structure
│       ├── components/      # React components
│       ├── hooks/           # Custom React hooks
│       ├── lib/             # Utility functions
│       ├── styles/          # Global styles
│       └── package.json
├── services/
│   ├── api/                 # FastAPI backend
│   │   ├── routes/          # API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   └── ai/                  # AI/ML services
│       ├── tutor/           # LLM + RAG
│       ├── evaluation/      # Essay/Speaking evaluation
│       └── recommendation/  # Recommendation engine
├── packages/
│   └── shared/              # Shared utilities
│       ├── types/           # Shared type definitions
│       └── constants/       # Shared constants
├── docs/
│   ├── prd.md              # Product requirements
│   ├── implementation.md    # Implementation guide
│   └── api.md              # API documentation
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Local development setup
├── package.json             # Root package file
├── pyproject.toml          # Python project config
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.11+
- Docker and Docker Compose
- OpenAI API key (for AI features)

### Local Development with Docker

1. **Clone the repository**
```bash
git clone <repo-url>
cd intelligent-test-prep-platform
```

2. **Set up environment variables**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
docker-compose exec api alembic upgrade head
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development (Without Docker)

#### Backend Setup

1. **Create Python virtual environment**
```bash
cd services/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r ../../requirements.txt
```

3. **Set up database**
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/testprep_db"
alembic upgrade head
```

4. **Run API server**
```bash
uvicorn services.api.main:app --reload
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd apps/web
npm install
```

2. **Run development server**
```bash
npm run dev
```

3. **Open browser**
- Navigate to http://localhost:3000

## 📚 API Documentation

Once the API is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

Key endpoints:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/users/me` - Get current user
- `GET /api/questions` - Get questions
- `POST /api/submissions` - Submit practice attempt
- `POST /api/chat` - Chat with AI tutor

## 🧪 Testing

### Run Backend Tests
```bash
pytest services/api/tests/
```

### Run Frontend Tests
```bash
cd apps/web
npm run test
```

### Run E2E Tests
```bash
cd apps/web
npm run e2e
```

## 🔧 Development Commands

### Root level (Monorepo)
```bash
npm run dev          # Start all services
npm run build        # Build all packages
npm run test         # Run all tests
npm run lint         # Lint all code
npm run format       # Format all code
```

### Backend
```bash
cd services/api
uvicorn main:app --reload
pytest
black .
isort .
mypy .
```

### Frontend
```bash
cd apps/web
npm run dev
npm run build
npm run test
npm run lint
```

## 📝 Documentation

- **Product Requirements**: [docs/prd.md](docs/prd.md)
- **Implementation Plan**: [docs/implementation.md](docs/implementation.md)
- **Task Tracking**: [tasks.md](tasks.md)
- **Progress**: [progress.md](progress.md)

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- CORS protection
- HTTPS in production
- Environment-based secret management

See [docs/security.md](docs/security.md) for detailed security guidelines.

## 🚢 Deployment

### Docker Build
```bash
docker-compose -f docker-compose.prod.yml build
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/
```

See [docs/deployment.md](docs/deployment.md) for detailed deployment instructions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Create a feature branch
2. Make changes
3. Run tests and linting
4. Submit a pull request

## 📊 Project Status

**Current Phase**: Phase 1 - Foundation (In Progress)

- [x] Project structure
- [x] Environment configuration
- [x] Database schema design
- [ ] Authentication system
- [ ] User profiles
- [ ] Dashboard
- [ ] (See [tasks.md](tasks.md) for complete task list)

## 🐛 Known Issues

None currently tracked. See [GitHub Issues](https://github.com/yourorg/repo/issues) for active issues.

## 📄 License

MIT License - see LICENSE file for details

## 👥 Team

- **Project Lead**: AI Agent
- **Architecture**: AI Agent
- **Development**: In Progress

## 📞 Support

For questions or issues:
1. Check [docs/](docs/) for documentation
2. Search [GitHub Issues](https://github.com/yourorg/repo/issues)
3. Create a new issue with detailed information

## 🗺️ Roadmap

### Q3 2024
- Phase 1: Foundation (Months 1-2)
- Phase 2: Core Learning (Months 2-3)

### Q4 2024
- Phase 3: AI Services (Months 4)
- Phase 4: Adaptive Learning (Months 5)

### Q1 2025
- Phase 5: Analytics & Polish (Months 6)
- Phase 6: Optimization & Launch (Months 7)

---

**Built with ❤️ for students worldwide**
