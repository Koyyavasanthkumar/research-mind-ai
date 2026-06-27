# Contributing

Thanks for improving ResearchMind AI.

## Development Setup

1. Create a Python virtual environment.
2. Install backend dependencies with `pip install -r requirements.txt`.
3. Install frontend dependencies with `npm ci` inside `frontend`.
4. Copy `.env.example` to `.env` and fill in local values.
5. Run `pytest backend/tests` before opening a pull request.
6. Run `npm run build` inside `frontend`.

## Pull Request Standards

- Keep changes scoped and documented.
- Add or update tests for API, workflow, database, and security behavior.
- Do not commit secrets, local databases, generated reports, Chroma stores, or logs.
- Include migration changes when database models change.

## Code Style

- Use typed Python and Pydantic validation for API boundaries.
- Keep agents single-purpose and communicate through `ResearchState`.
- Prefer service and repository layers over database work inside route handlers.
