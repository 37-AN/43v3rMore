# Coding Standards

## Python Style
- PEP 8 compliance (enforced by Black formatter)
- Type hints for all function signatures
- Docstrings (Google style) for all public functions
- Max line length: 88 characters (Black default)
- Use pathlib for file operations
- Prefer f-strings for formatting

## Code Organization
```python
# Order of imports
import standard_library
import third_party
import local_modules

# Class structure
class MyClass:
    """Class docstring."""

    # Class variables
    CLASS_VAR = "value"

    def __init__(self):
        """Initialize."""
        pass

    # Public methods
    def public_method(self):
        """Public method."""
        pass

    # Private methods
    def _private_method(self):
        """Private helper."""
        pass
```

## Error Handling
```python
# Always use specific exceptions
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
finally:
    cleanup()
```

## Logging
```python
from loguru import logger

# Use appropriate levels
logger.debug("Detailed info for debugging")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")

# Include context
logger.info(f"Processing {symbol}", extra={
    "symbol": symbol,
    "user_id": user_id
})
```

## Testing
- Minimum 80% code coverage
- Test file naming: test_{module}.py
- Use pytest fixtures for setup
- Mock external dependencies
- Test edge cases and errors
