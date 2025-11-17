# Claude Custom Instructions - 43v3rMore Project

## Core Principles

### 1. Token Efficiency & Resource Optimization
- **Read Before Edit**: Always read files before editing to understand context
- **Targeted Operations**: Use specific file paths instead of broad searches when possible
- **Batch Operations**: Combine related tool calls in parallel when independent
- **Minimal Output**: Be concise; avoid verbose explanations unless requested
- **Smart Caching**: Leverage conversation context instead of re-reading files
- **Progressive Disclosure**: Start with high-level, drill down only when needed

### 2. Prompt Engineering Best Practices
- **Clarity First**: Request clarification before making assumptions
- **Context Gathering**: Read relevant files to understand existing patterns
- **Pattern Matching**: Follow existing code style, naming conventions, and architecture
- **Incremental Changes**: Make small, testable changes rather than large rewrites
- **Explicit Validation**: Confirm understanding of requirements before implementation
- **Error Context**: When errors occur, provide file:line references for quick navigation

### 3. Development Excellence

#### Code Quality
```python
# ✓ GOOD: Type hints, docstrings, error handling
def calculate_quantum_signal(
    qubits: int,
    theta: float,
    backend: str = "ibmq_qasm_simulator"
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate quantum phase estimation for market signal.

    Args:
        qubits: Number of qubits for QPE circuit
        theta: Phase angle for estimation
        backend: IBM Quantum backend to use

    Returns:
        Tuple of (estimated_phase, circuit_metrics)

    Raises:
        QuantumError: If circuit execution fails
        ValueError: If invalid parameters provided
    """
    try:
        circuit = create_qpe_circuit(qubits, theta)
        result = execute_circuit(circuit, backend)
        return process_results(result)
    except QiskitError as e:
        logger.error(f"Quantum execution failed: {e}", extra={
            "qubits": qubits, "theta": theta, "backend": backend
        })
        raise QuantumError(f"QPE calculation failed: {e}") from e

# ✗ BAD: No types, no docs, poor error handling
def calc(q, t, b="sim"):
    c = make_circuit(q, t)
    r = run(c, b)
    return process(r)
```

#### Architecture Adherence
- **Separation of Concerns**: Keep business logic, data access, and presentation separate
- **Dependency Injection**: Use DI for testability and flexibility
- **Interface Segregation**: Define clear interfaces/protocols for components
- **Single Responsibility**: Each function/class should do one thing well
- **DRY Principle**: Extract common patterns into reusable utilities

#### Security First
```python
# ✓ GOOD: Proper secrets management
from config import get_secret

api_key = get_secret("ANTHROPIC_API_KEY")  # From env/vault
client = anthropic.Anthropic(api_key=api_key)

# ✗ BAD: Hardcoded secrets
api_key = "sk-ant-api03-hardcoded-secret"  # NEVER DO THIS

# ✓ GOOD: Input validation
def place_trade(symbol: str, amount: float):
    if not re.match(r'^[A-Z]{3,6}$', symbol):
        raise ValueError(f"Invalid symbol: {symbol}")
    if not 0 < amount <= MAX_TRADE_SIZE:
        raise ValueError(f"Invalid amount: {amount}")

# ✗ BAD: No validation (SQL injection, command injection risk)
def place_trade(symbol, amount):
    db.execute(f"INSERT INTO trades VALUES ('{symbol}', {amount})")
```

### 4. AI-Assisted Development Guidelines

#### When to Use AI
- **Boilerplate Generation**: Create standard CRUD operations, API endpoints
- **Test Generation**: Generate test cases based on function signatures
- **Documentation**: Auto-generate docstrings, README sections
- **Code Analysis**: Review security, performance, style issues
- **Refactoring**: Suggest improvements to existing code
- **Debugging**: Analyze error logs and suggest fixes

#### When NOT to Use AI
- **Sensitive Logic**: Critical financial calculations (verify manually)
- **Security Decisions**: Authentication, authorization logic (expert review required)
- **Architecture Changes**: Major structural changes (team discussion needed)
- **Production Hotfixes**: Critical fixes under time pressure (manual review)

#### AI Tool Usage Strategy
```bash
# Search Strategy (token-efficient)
1. Use Glob for filename patterns: **/*.py, src/quantum/**
2. Use Grep for code patterns: "class.*Engine", "def.*signal"
3. Read only relevant files, not entire directories
4. Use Task tool for complex multi-file exploration

# Testing Strategy
1. Run tests before changes: pytest -v
2. Run specific test file: pytest tests/test_quantum.py
3. Run with coverage: pytest --cov=src --cov-report=html
4. Fix failures incrementally, don't batch

# Git Strategy
1. Check status: git status
2. Review changes: git diff
3. Stage selectively: git add <specific-files>
4. Commit with context: git commit -m "type(scope): clear message"
5. Push to feature branch: git push -u origin claude/feature-name
```

### 5. Token Usage Optimization

#### Efficient File Operations
```python
# ✓ GOOD: Read specific sections
Read(file_path="/path/to/large_file.py", offset=100, limit=50)

# ✓ GOOD: Use Grep to find before reading
Grep(pattern="class QuantumEngine", path="src/")
# Then read only matched files

# ✗ BAD: Read entire large file when you only need one function
Read(file_path="/path/to/10000_line_file.py")
```

#### Smart Context Management
- **Reference by Location**: Use file:line format (e.g., `src/quantum.py:142`)
- **Avoid Repetition**: Don't re-explain what was discussed in context
- **Lazy Loading**: Only fetch details when specifically needed
- **Structured Output**: Use tables, lists for dense information

#### Parallel Operations
```python
# ✓ GOOD: Run independent operations in parallel
<function_calls>
  <invoke name="Read"><parameter name="file_path">src/file1.py
# ✗ BAD: Sequential when could be parallel
Read file1, wait... Read file2, wait... Run tests, wait...
```

### 6. Performance Optimization

#### Database Queries
```python
# ✓ GOOD: Efficient query with indexing
@db_session
def get_recent_signals(symbol: str, limit: int = 100):
    return select(
        s for s in Signal 
        where s.symbol == symbol 
        order_by desc(s.timestamp)
    ).limit(limit)

# ✗ BAD: Loading all records then filtering
signals = Signal.select().all()
filtered = [s for s in signals if s.symbol == symbol][:100]
```

#### Caching Strategy
```python
from functools import lru_cache
from cachetools import TTLCache

# Cache expensive computations
@lru_cache(maxsize=128)
def calculate_indicator(symbol: str, period: int) -> float:
    """Cached indicator calculation."""
    return expensive_calculation(symbol, period)

# Time-based cache for market data
market_cache = TTLCache(maxsize=1000, ttl=60)  # 60 second TTL

def get_market_data(symbol: str) -> dict:
    if symbol in market_cache:
        return market_cache[symbol]
    data = fetch_from_mt5(symbol)
    market_cache[symbol] = data
    return data
```

#### Async Operations
```python
# ✓ GOOD: Concurrent API calls
async def fetch_multiple_symbols(symbols: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_symbol(session, symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# ✗ BAD: Sequential API calls
def fetch_multiple_symbols(symbols: List[str]):
    results = []
    for symbol in symbols:
        results.append(fetch_symbol(symbol))  # Blocking
    return results
```

### 7. Testing Best Practices

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

def test_quantum_signal_calculation():
    """Test QPE signal calculation with mock quantum backend."""
    # Arrange
    mock_backend = Mock()
    mock_backend.run.return_value = {"counts": {"111": 950, "000": 50}}
    
    # Act
    result = calculate_quantum_signal(
        qubits=3, 
        theta=0.875, 
        backend=mock_backend
    )
    
    # Assert
    assert 0.85 <= result <= 0.90
    mock_backend.run.assert_called_once()

@pytest.fixture
def mock_mt5_connection():
    """Fixture for mocked MT5 connection."""
    with patch('MetaTrader5.initialize') as mock_init:
        mock_init.return_value = True
        yield mock_init
```

#### Integration Tests
```python
@pytest.mark.integration
def test_end_to_end_signal_generation(test_db):
    """Test complete signal generation pipeline."""
    # Setup
    signal_generator = SignalGenerator(db=test_db)
    
    # Execute
    signal = signal_generator.generate(
        symbol="EURUSD",
        timeframe="H1"
    )
    
    # Verify
    assert signal.symbol == "EURUSD"
    assert signal.confidence >= 0.95
    assert signal.timestamp is not None
    
    # Cleanup
    test_db.rollback()
```

### 8. Documentation Standards

#### Code Documentation
```python
def execute_trade(
    symbol: str,
    action: Literal["BUY", "SELL"],
    volume: float,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None
) -> TradeResult:
    """
    Execute a trade on MetaTrader 5 platform.

    This function places a market order with optional stop loss and take profit
    levels. It includes retry logic for connection failures and validates all
    parameters before execution.

    Args:
        symbol: Trading symbol (e.g., "EURUSD", "GBPUSD")
        action: Trade direction, either "BUY" or "SELL"
        volume: Lot size (0.01 to 100.0)
        stop_loss: Stop loss price level (optional)
        take_profit: Take profit price level (optional)

    Returns:
        TradeResult object containing:
            - order_id: MT5 order ticket number
            - execution_price: Actual fill price
            - execution_time: Timestamp of execution
            - status: "SUCCESS" or "FAILED"

    Raises:
        MT5ConnectionError: If connection to MT5 fails
        InvalidParameterError: If parameters are invalid
        InsufficientMarginError: If account has insufficient margin
        
    Example:
        >>> result = execute_trade(
        ...     symbol="EURUSD",
        ...     action="BUY",
        ...     volume=0.1,
        ...     stop_loss=1.0850,
        ...     take_profit=1.0950
        ... )
        >>> print(f"Order ID: {result.order_id}")
        Order ID: 123456789

    Note:
        - Requires active MT5 connection
        - Validates symbol exists and is tradable
        - Checks margin requirements before execution
        - Logs all trades for audit trail
    """
    # Implementation...
```

#### API Documentation
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

app = FastAPI(
    title="Quantum Trading API",
    description="AI-powered trading signals using quantum computing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class SignalRequest(BaseModel):
    """Request model for signal generation."""
    
    symbol: str = Field(
        ..., 
        description="Trading pair (e.g., EURUSD)",
        pattern="^[A-Z]{6}$",
        example="EURUSD"
    )
    timeframe: str = Field(
        ...,
        description="Chart timeframe (M1, M5, M15, H1, H4, D1)",
        pattern="^(M1|M5|M15|M30|H1|H4|D1)$",
        example="H1"
    )

@app.post(
    "/api/v1/signals",
    response_model=SignalResponse,
    tags=["signals"],
    summary="Generate trading signal",
    description="Generate AI-powered trading signal using quantum computing"
)
async def generate_signal(
    request: SignalRequest,
    api_key: str = Depends(verify_api_key)
) -> SignalResponse:
    """
    Generate a trading signal for the specified symbol and timeframe.
    
    This endpoint uses quantum phase estimation to detect market cycles
    and generates high-confidence trading signals (95%+ accuracy).
    
    **Rate Limit**: 100 requests per hour per API key
    
    **Response Time**: Typically 2-5 seconds
    """
    # Implementation...
```

### 9. Error Handling & Logging

#### Structured Logging
```python
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    level="DEBUG"
)

# Contextual logging
def process_signal(signal_id: str):
    with logger.contextualize(signal_id=signal_id):
        logger.info("Processing signal")
        try:
            result = calculate_signal()
            logger.success(f"Signal processed: {result}")
        except Exception as e:
            logger.exception(f"Signal processing failed")
            raise
```

#### Error Recovery
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def connect_to_mt5() -> bool:
    """
    Connect to MT5 with automatic retry logic.
    
    Retries up to 3 times with exponential backoff:
    - Attempt 1: immediate
    - Attempt 2: wait 2 seconds
    - Attempt 3: wait 4 seconds
    """
    logger.info("Attempting MT5 connection")
    if not MT5.initialize():
        error = MT5.last_error()
        logger.warning(f"MT5 connection failed: {error}")
        raise MT5ConnectionError(f"Connection failed: {error}")
    
    logger.success("MT5 connected successfully")
    return True
```

### 10. Project-Specific Guidelines

#### Quantum Computing
- **QPE Accuracy**: Maintain 95%+ accuracy on all backtests
- **Circuit Optimization**: Keep qubit count ≤ 5 for IBM free tier
- **Error Mitigation**: Always use readout error mitigation
- **Backend Selection**: Use `ibmq_qasm_simulator` for development, real hardware for production

#### Trading Logic
- **Risk Management**: Never risk >1% of capital per trade
- **Signal Validation**: Require ≥0.95 confidence before trading
- **Position Sizing**: Use Kelly Criterion for optimal sizing
- **Stop Loss**: Always set stop loss at signal generation
- **Max Drawdown**: Circuit breaker at 10% daily drawdown

#### API Design
- **Versioning**: Use /api/v1/ prefix for all endpoints
- **Rate Limiting**: Enforce per-user limits (100 req/hour)
- **Authentication**: JWT tokens with 24-hour expiry
- **Error Responses**: Return RFC 7807 Problem Details
- **Pagination**: Use cursor-based pagination for lists

#### Deployment
- **Docker**: All services must be containerized
- **Environment**: Use .env files (never commit secrets)
- **Health Checks**: Implement /health and /ready endpoints
- **Monitoring**: Log metrics to console (JSON format)
- **Graceful Shutdown**: Handle SIGTERM properly

### 11. Communication Style

#### Code Comments
```python
# ✓ GOOD: Explains WHY, not WHAT
# Use QPE instead of FFT because it provides 99% vs 87% accuracy
# as validated in MQL5 Article 17171 backtests
result = quantum_phase_estimation(data)

# ✗ BAD: Explains obvious code
# Calculate the result using quantum phase estimation
result = quantum_phase_estimation(data)
```

#### Commit Messages
```bash
# ✓ GOOD: Clear, contextual, follows convention
feat(quantum): implement error mitigation for QPE

Add readout error mitigation to improve QPE accuracy from 93% to 96%.
Uses built-in Qiskit mitigation calibration with 3-qubit calibration matrix.

Closes #42

# ✗ BAD: Vague, no context
fixed stuff
```

#### User Communication
- **Be Direct**: State facts clearly, avoid hedging unless genuinely uncertain
- **Provide Context**: Include file:line references for code locations
- **Offer Options**: When multiple approaches exist, present pros/cons
- **Admit Uncertainty**: Say "I need to investigate" rather than guessing
- **Next Steps**: Always end with clear next action

### 12. Quality Checklist

Before committing code, verify:

- [ ] **Type Hints**: All functions have type annotations
- [ ] **Docstrings**: All public functions documented (Google style)
- [ ] **Tests**: Unit tests written, passing, >80% coverage
- [ ] **Logging**: Appropriate log levels used
- [ ] **Error Handling**: Specific exceptions, proper recovery
- [ ] **Security**: No hardcoded secrets, input validated
- [ ] **Performance**: No obvious bottlenecks (N+1 queries, etc.)
- [ ] **Formatting**: Code formatted with Black/Prettier
- [ ] **Linting**: No errors from flake8/mypy/eslint
- [ ] **Documentation**: README/docs updated if needed
- [ ] **Git**: Clear commit message, feature branch used
- [ ] **Review**: Self-review diff before committing

### 13. Anti-Patterns to Avoid

#### Code Smells
```python
# ✗ BAD: God class (too many responsibilities)
class TradingSystem:
    def connect_mt5(self): ...
    def run_quantum_circuit(self): ...
    def send_telegram(self): ...
    def process_payment(self): ...
    def generate_report(self): ...

# ✓ GOOD: Single responsibility per class
class MT5Connector: ...
class QuantumEngine: ...
class NotificationService: ...
class BillingService: ...
class ReportGenerator: ...

# ✗ BAD: Magic numbers
if confidence > 0.87:  # Why 0.87?
    execute_trade()

# ✓ GOOD: Named constants
MINIMUM_CONFIDENCE_THRESHOLD = 0.95  # From backtest validation
if confidence > MINIMUM_CONFIDENCE_THRESHOLD:
    execute_trade()

# ✗ BAD: Swallowing exceptions
try:
    risky_operation()
except:
    pass  # Silently fails!

# ✓ GOOD: Explicit error handling
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    notify_admin(e)
    raise  # Re-raise for upstream handling
```

#### Architecture Anti-Patterns
- **Premature Optimization**: Don't optimize until you measure
- **Over-Engineering**: Build for today's needs, not imagined futures
- **Tight Coupling**: Depend on interfaces, not concrete implementations
- **No Separation**: Keep API, business logic, and data layers separate
- **Implicit Dependencies**: Use dependency injection, not globals

---

## Quick Reference

### File Operations Priority
1. **Glob** - Find files by pattern
2. **Grep** - Search code content
3. **Read** - Read specific file (use offset/limit for large files)
4. **Edit** - Modify existing file
5. **Write** - Create new file (only when necessary)

### Testing Workflow
```bash
pytest                              # Run all tests
pytest tests/test_quantum.py -v    # Run specific test
pytest --cov=src --cov-report=html # With coverage
pytest -k "test_signal" -v         # Run tests matching pattern
```

### Git Workflow
```bash
git status                          # Check current state
git diff                            # Review changes
git add src/quantum/engine.py       # Stage specific files
git commit -m "feat(quantum): ..."  # Commit with message
git push -u origin claude/feature   # Push to feature branch
```

### Common Commands
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/
mypy src/

# Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

# Docker
docker build -t quantum-trading .
docker-compose up -d
docker-compose logs -f
```

---

## Summary

**Core Philosophy**: Write clear, secure, tested code that follows project patterns. Optimize for maintainability and token efficiency. Communicate directly with context. Leverage AI for acceleration, but verify critical logic manually.

**When in Doubt**:
1. Read existing code to understand patterns
2. Ask for clarification rather than guessing
3. Start small, iterate based on feedback
4. Test before committing
5. Document your decisions

**Remember**: You're building a production trading system handling real money. Accuracy and security are non-negotiable. Every line of code should be intentional and tested.
