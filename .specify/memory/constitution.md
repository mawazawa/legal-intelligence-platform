# Legal Intelligence Platform Constitution
<!-- JusticeOS™-aligned constitutional principles for legal technology -->

## Core Principles

### I. Empathy-First Design (NON-NEGOTIABLE)
Self-represented litigants are the primary users, not lawyers. Every feature must assume users are in crisis, experiencing trauma, or under time pressure. Cognitive load and emotional burden must be minimized at every interaction point.

### II. Accessibility Excellence (NON-NEGOTIABLE)
WCAG AAA compliance required (not AA). Mobile-first design assumes slow connections and older devices. Screen reader compatibility tested with NVDA/JAWS. Color contrast ratios must exceed 7:1. No accessibility shortcuts or "good enough" compromises.

### III. Performance Budgets (NON-NEGOTIABLE)
Initial page load: <3 seconds on 3G. Time to Interactive: <5 seconds. 60fps animations with no jank during stress. Bundle size: <200KB initial JS. Every millisecond matters when users are under pressure.

### IV. Evidence-Based Development (NON-NEGOTIABLE)
No "should work" without Playwright verification. All legal claims backed by case law citations (Shepardized). User testing with actual self-represented litigants before merge. No assumptions about user behavior without data.

### V. Trauma-Informed UX (NON-NEGOTIABLE)
No aggressive CTAs or dark patterns. Clear escape routes from any workflow. Progress auto-saves (never lose work during crisis). Plain language (8th grade reading level max). Every interaction must feel safe and supportive.

### VI. Security & Privacy (NON-NEGOTIABLE)
All PII encrypted at rest. No third-party trackers or analytics without explicit consent. Document retention policies aligned with California court rules. Privacy by design, not as an afterthought.

## Project Context

### Legal Intelligence Platform Scope
- Email parsing and contact extraction from .mbox files
- CSV deduplication for contact management  
- Evidence organization from Google Takeout exports
- Integration with existing case files (FDI-21-794666, FDV-24-817888, A171270)

### Demo Success Criteria (Pre-JusticeOS Merge)
- Successfully parse and deduplicate contacts from 20+ email threads
- Generate participant scorecards with response metrics
- Maintain all git history for audit trail
- Zero breaking changes when merged into JusticeOS repo

### Non-Negotiable Quality Gates
- All Python scripts must pass `ruff check` with zero errors
- All CSV exports must validate against schema
- Git commits must include descriptive messages (no "fix" or "update")
- Documentation must be current (no stale README content)

## Development Workflow

### Test-Driven Development
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. No code without tests, no tests without user validation.

### Integration Testing Focus
New library contract tests, Contract changes, Inter-service communication, Shared schemas. Legal data integrity requires bulletproof integration testing.

### Code Quality Standards
- Python: `ruff check` with zero errors, type hints required
- Documentation: Current, user-tested, plain language
- Git: Descriptive commits, atomic changes, audit trail
- Performance: Measured, not assumed

## Governance

Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan. All PRs/reviews must verify compliance with JusticeOS™ principles. Complexity must be justified with user benefit. Use `.specify/memory/constitution.md` for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-10-17 | **Last Amended**: 2025-10-17