# Development Workflow

## Git Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

## Commit Message Format
```
type(scope): subject

body (optional)

footer (optional)
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat(quantum): implement QPE algorithm

Add quantum phase estimation for market cycle detection
using Qiskit. Achieves 95%+ accuracy on backtests.

Closes #123
```

## Development Process
1. **Plan**: Review requirements, design solution
2. **Branch**: Create feature branch from develop
3. **Implement**: Write code following standards
4. **Test**: Unit tests, integration tests
5. **Document**: Update docs, add docstrings
6. **Review**: Self-review checklist
7. **Commit**: Clear commit messages
8. **Push**: Push to remote
9. **Deploy**: Merge to develop, then main

## Testing Strategy
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_quantum_engine.py -v

# Run integration tests
pytest tests/integration/ -v
```

## Code Review Checklist
- [ ] Code follows style guide
- [ ] All functions have docstrings
- [ ] Tests written and passing
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Logging added appropriately
- [ ] Performance considered
- [ ] Security reviewed
- [ ] Documentation updated

## Deployment Process
```bash
# 1. Run tests
pytest

# 2. Build Docker image
docker build -t quantum-trading:latest .

# 3. Run locally
docker-compose up

# 4. Deploy to production
./scripts/deploy.sh production

# 5. Monitor
./scripts/monitor.py --env production
```

## Changelog Updates
Update CHANGELOG.md after each feature/fix:
```markdown
## [1.2.0] - 2025-12-01
### Added
- Quantum Phase Estimation algorithm
- Telegram signal delivery
- Automated billing system

### Changed
- Improved signal accuracy to 96%
- Optimized database queries

### Fixed
- MT5 connection timeout issue
- Telegram rate limiting
```
