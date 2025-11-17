# Claude Code Configuration

This directory contains configuration files and custom instructions for Claude Code AI assistant to ensure consistent, high-quality development practices throughout the 43v3rMore project.

## Files Overview

### `custom_instructions.md` ⭐
**Comprehensive AI development guidelines** covering:
- Token efficiency & resource optimization
- Prompt engineering best practices
- Code quality standards
- AI-assisted development workflows
- Security, performance, and testing guidelines
- Project-specific rules for quantum trading system

**Usage**: These instructions are automatically applied to Claude Code sessions to ensure consistent development patterns, optimize token usage, and maintain high code quality.

### `project_context.md`
**High-level project overview**:
- Mission and business model
- Core technology stack (Quantum + AI + MT5)
- Key constraints (zero capital, free tier)
- Success metrics and timeline

### `development_workflow.md`
**Git and development processes**:
- Branching strategy
- Commit message format
- Testing workflow
- Code review checklist
- Deployment process

### `coding_standards.md`
**Python coding conventions**:
- PEP 8 compliance
- Type hints and docstrings
- Error handling patterns
- Logging standards
- Testing requirements

### `architecture.md`
**System architecture documentation**:
- Component structure
- Data flow patterns
- Integration points
- Scalability considerations

## How These Files Work

When you start a Claude Code session, these files provide context that helps Claude:

1. **Understand the project** - Mission, constraints, technology stack
2. **Follow conventions** - Coding standards, commit formats, architecture patterns
3. **Optimize efficiency** - Token usage, parallel operations, targeted searches
4. **Ensure quality** - Security checks, testing requirements, error handling
5. **Make better decisions** - When to use AI, what to verify manually, anti-patterns to avoid

## Key Benefits

### 🚀 Faster Development
- Reduced back-and-forth clarifications
- Consistent code patterns across sessions
- Optimized tool usage (fewer tokens, faster responses)

### 🎯 Higher Quality
- Security-first approach (no hardcoded secrets, input validation)
- Comprehensive error handling and logging
- Test-driven development enforced
- Documentation standards maintained

### 💰 Cost Efficiency
- Token optimization strategies
- Parallel operations where possible
- Targeted file operations (Grep before Read)
- Smart context management

### 🔒 Production-Ready
- Trading system-specific safety checks (risk management, confidence thresholds)
- Quantum computing best practices (circuit optimization, error mitigation)
- Real-money handling safeguards
- Audit trail requirements

## Customization

Feel free to update these files as the project evolves:

- **Add new patterns** - Document new architectural patterns as they emerge
- **Update constraints** - Modify resource limits, accuracy targets, etc.
- **Refine guidelines** - Improve based on lessons learned
- **Project-specific rules** - Add domain-specific requirements

## Example: How Instructions Improve Development

### Without Custom Instructions
```
User: Add a new trading signal endpoint
Claude: Creates basic endpoint, no validation, generic error handling
Result: Security issues, inconsistent with project patterns, requires multiple revisions
```

### With Custom Instructions
```
User: Add a new trading signal endpoint
Claude:
- Follows existing API pattern (/api/v1/ prefix)
- Adds input validation (symbol format, timeframe enum)
- Implements rate limiting (100 req/hour)
- Uses JWT authentication
- Returns RFC 7807 Problem Details for errors
- Includes comprehensive docstring with examples
- Adds unit tests with 80%+ coverage
- Logs with structured context
Result: Production-ready code in first iteration
```

## Quick Reference

### When Claude Should Read These Files
Claude automatically has access to these instructions, but you can reference them explicitly:

- "Follow the custom instructions"
- "Use the coding standards from .claude/"
- "Check the project context"

### Updating Instructions
```bash
# Edit custom instructions
nano .claude/custom_instructions.md

# Commit changes
git add .claude/
git commit -m "docs(claude): update custom instructions for new API patterns"
git push
```

## Best Practices

1. **Keep Instructions Updated** - As project evolves, update these files
2. **Be Specific** - Add project-specific examples and patterns
3. **Reference Real Code** - Point to actual implementations as examples
4. **Document Decisions** - Explain why certain patterns are preferred
5. **Include Anti-Patterns** - Show what NOT to do

## Token Usage Impact

These instructions are included in every Claude Code session context. To keep token usage efficient:

- ✅ Keep instructions actionable and concise
- ✅ Use code examples (dense information)
- ✅ Reference file locations instead of duplicating code
- ❌ Avoid verbose explanations
- ❌ Don't duplicate information from code comments

## Contributing

When adding new guidelines:

1. **Validate** - Ensure the pattern has proven effective
2. **Example** - Include code examples (good/bad)
3. **Context** - Explain when to apply the pattern
4. **Test** - Verify Claude follows the new instruction

## Questions?

If Claude isn't following these instructions:
- Explicitly reference the relevant section
- Ask Claude to confirm understanding
- Update instructions to be more specific
- Provide concrete examples

---

**Last Updated**: 2025-11-17
**Maintained By**: 37-AN
**Project**: 43v3rMore Quantum Trading System
