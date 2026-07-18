# Contributing Guidelines

## Code of Conduct

We are committed to maintaining a respectful and inclusive community. All contributors are expected to follow these principles:
- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Report inappropriate behavior

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch from `main`
4. Make your changes
5. Run tests and linting
6. Submit a pull request

## Development Setup

### Prerequisites
- Node.js 18+ and npm 9+
- Python 3.11+
- Docker and Docker Compose
- Git

### Local Setup
```bash
# Clone and install
git clone https://github.com/yourorg/repo.git
cd intelligent-test-prep-platform

# Copy environment file
cp .env.example .env.local

# Install dependencies
npm install
pip install -r requirements.txt

# Start development environment
docker-compose up -d
```

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements
- `test/description` - Testing improvements

## Commit Messages

Follow conventional commits:
- `feat: add new feature`
- `fix: resolve issue`
- `docs: update documentation`
- `refactor: improve code`
- `test: add tests`
- `chore: maintenance tasks`

Example: `feat: implement AI tutor chat endpoint`

## Pull Request Process

1. **Update Documentation** - Update relevant docs
2. **Add Tests** - Include tests for changes
3. **Run Linting** - Ensure code quality
4. **Keep it Small** - Focus on one feature
5. **Descriptive PR** - Explain what and why

## Code Style

### TypeScript/JavaScript
- Use Prettier for formatting
- Use ESLint for linting
- Strict TypeScript types
- Functional components (React)
- Use TypeScript for all files

```bash
cd apps/web
npm run lint
npm run format
npm run type-check
```

### Python
- PEP 8 style guide
- Type hints required
- Docstrings for functions
- Black for formatting
- MyPy for type checking

```bash
black services/
isort services/
mypy services/
flake8 services/
```

## Testing Requirements

### Backend
- Minimum 80% code coverage
- Unit tests required
- Integration tests for APIs
- Run: `pytest services/api/tests/`

### Frontend
- Component tests for all components
- Hook tests for custom hooks
- E2E tests for critical flows
- Run: `npm run test`

## Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Breaking change

## How to Test
Steps to test the changes

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
Add screenshots for UI changes
```

## Review Process

1. **Automated Checks** - GitHub Actions run tests
2. **Code Review** - Maintainers review code
3. **Address Feedback** - Make requested changes
4. **Merge** - Approved PRs are merged

## Documentation Standards

All code should include:
- Function/class docstrings
- Type hints
- Usage examples for complex features
- Update relevant docs in `/docs` folder

### Backend Docstring Example
```python
def evaluate_essay(text: str, prompt: str) -> EssayEvaluation:
    """
    Evaluate student essay against prompt.
    
    Args:
        text: The essay text to evaluate
        prompt: The essay prompt/question
        
    Returns:
        EssayEvaluation object with scores and feedback
        
    Raises:
        ValueError: If text or prompt is empty
    """
```

### Frontend Documentation Example
```typescript
/**
 * Displays a reading practice question with passage
 * @param question - The question data
 * @param onSubmit - Callback when answer is submitted
 * @returns React component
 */
export function ReadingQuestion({ question, onSubmit }: Props) {
```

## Database Changes

When modifying the database schema:

1. Create Alembic migration:
```bash
alembic revision --autogenerate -m "description"
```

2. Review generated migration file
3. Test migration and rollback
4. Include migration in PR

## Performance Considerations

- Avoid N+1 queries
- Use indexes for frequent queries
- Cache appropriately
- Lazy load components/modules
- Minimize bundle size
- Profile before optimizing

## Security Guidelines

- Never commit secrets
- Use environment variables for sensitive data
- Validate all inputs
- Sanitize outputs
- Use HTTPS in production
- Follow OWASP guidelines
- Regular dependency updates

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

1. Update version in `package.json` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag vX.Y.Z`
4. Push tag: `git push origin vX.Y.Z`
5. Create GitHub Release with notes

## Questions or Need Help?

- Open a discussion in GitHub
- Check existing issues
- Review documentation
- Ask in community chat

## Recognition

All contributors will be recognized in:
- `CONTRIBUTORS.md`
- Release notes
- Project README

---

Thank you for contributing! Your work makes this platform better for students everywhere. 🚀
