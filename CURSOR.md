# Legal Intelligence Platform Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-17

## Active Technologies
- Python 3.11+ (contact extraction, deduplication)
- Git (version control with audit trail)
- CSV processing (contact management)
- .mbox email parsing
- GitHub Spec-Kit (specification-driven development)

## Project Structure
```
legal-intelligence-platform/
├── .specify/                   # Spec-Kit framework
│   ├── memory/
│   │   └── constitution.md     # JusticeOS™ principles
│   ├── templates/              # Feature templates
│   └── scripts/               # Automation helpers
├── specs/                     # Feature specifications
│   ├── 001-contact-extraction/
│   └── 002-email-deduplication/
├── src/                       # Application source code
├── docker/                    # Containerization setup
├── extract_contacts.py        # Email parsing tool
├── deduplicate_contacts.py    # CSV deduplication
└── persons-log.csv           # Contact database
```

## Commands

### Spec-Kit Slash Commands (Cursor AI)
- `/speckit.constitution` - Review/update governing principles
- `/speckit.specify` - Create new feature specification
- `/speckit.plan` - Generate technical implementation plan
- `/speckit.tasks` - Break down into atomic tasks
- `/speckit.implement` - Execute tasks with TDD
- `/speckit.clarify` - Ask structured questions to de-risk ambiguous areas
- `/speckit.analyze` - Cross-artifact consistency & alignment report
- `/speckit.checklist` - Generate quality checklists

### Development Commands
```bash
# Contact extraction
python3 extract_contacts.py

# CSV deduplication
python3 deduplicate_contacts.py

# Code quality
ruff check .

# Git workflow
git add .
git commit -m "Descriptive message"
git push origin main
```

## Code Style

### Python Standards
- Use `ruff` for linting (zero errors required)
- Type hints required for all functions
- Docstrings for all public functions
- Follow PEP 8 with 88-character line limit
- Use f-strings for string formatting

### Git Standards
- Descriptive commit messages (no "fix" or "update")
- Atomic commits (one logical change per commit)
- Maintain audit trail for legal compliance
- Use conventional commit format when possible

### JusticeOS™ Quality Gates
- WCAG AAA compliance (not AA)
- <3 second page loads on 3G
- 60fps animations with no jank
- <200KB initial JS bundle
- Plain language (8th grade reading level)
- Trauma-informed UX patterns

## Recent Changes

### Feature 1: Contact Extraction (001-contact-extraction)
- Added `extract_contacts.py` for automated .mbox parsing
- Extracts names, emails, phone numbers, roles from email signatures
- Handles multiple email formats and encoding issues
- Outputs clean CSV format for contact management

### Feature 2: Email Deduplication (002-email-deduplication)
- Added `deduplicate_contacts.py` for CSV cleaning
- Merges duplicate entries with multiple email addresses
- Preserves all contact information during deduplication
- Maintains alphabetical sorting

### Feature 3: Spec-Kit Framework Integration
- Initialized GitHub Spec-Kit with Claude AI
- Created JusticeOS™-aligned constitutional principles
- Set up specification-driven development workflow
- Prepared for safe JusticeOS repo integration

## Manual Additions

### Legal Intelligence Platform Context
This project processes legal evidence from Google Takeout exports, specifically:
- Case files: FDI-21-794666, FDV-24-817888, A171270
- Email evidence from divorce proceedings (2019-2022)
- Contact management for legal professionals
- Participant scorecards with response metrics

### Demo Success Criteria
Before merging into JusticeOS repo:
- Successfully parse and deduplicate contacts from 20+ email threads
- Generate participant scorecards with response metrics
- Maintain all git history for audit trail
- Zero breaking changes when merged into JusticeOS repo

### Non-Negotiable Quality Gates
- All Python scripts must pass `ruff check` with zero errors
- All CSV exports must validate against schema
- Git commits must include descriptive messages
- Documentation must be current (no stale README content)
- All legal claims backed by case law citations (Shepardized)
- User testing with actual self-represented litigants before merge

### Crisis-Aware Development
- Assume users are in crisis, experiencing trauma, or under time pressure
- Every feature must reduce cognitive load and emotional burden
- No aggressive CTAs or dark patterns
- Clear escape routes from any workflow
- Progress auto-saves (never lose work during crisis)
- Plain language (8th grade reading level max)
