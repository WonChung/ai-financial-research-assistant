# Security

This project is a local development prototype for financial research and education. It is not a production financial application.

## API Keys

API keys and secrets belong in `.env` files, not in source code.

Backend:

```bash
cd backend
cp .env.example .env
```

Frontend:

```bash
cd frontend
cp .env.example .env
```

Do not hardcode real API keys in Python, TypeScript, tests, shell commands, screenshots, or documentation.

## Ignored Environment Files

`.env` files are ignored by git. Keep them out of commits.

Ignored examples:

- `.env`
- `backend/.env`
- `frontend/.env`

Before committing, check:

```bash
git status --short
```

## Financial and Account Data

Do not upload real financial account data to this app.

Avoid uploading:

- brokerage statements
- bank statements
- tax documents
- personally identifiable information
- confidential client or employer materials
- account numbers or credentials

Uploaded documents and vector records are stored locally under `backend/data/`. This local storage is useful for development, but it is not designed as secure document storage.

## Research and Education Only

This application is for research and education only.

It can help organize document-backed research and summarize simple portfolio concentration risks from user-entered data, but it does not understand a user's full financial situation.

## No Investment Advice

This app does not provide investment advice, financial advice, tax advice, legal advice, trading recommendations, or buy/sell recommendations.

Do not use this app as the sole basis for investment, trading, tax, legal, or financial planning decisions.

## Not Production Hardened

The prototype does not include:

- authentication
- authorization
- encrypted document storage
- secure file scanning
- audit logging
- rate limiting
- production secret management
- production database migrations
- deployment hardening

Those controls would be required before handling sensitive data or deploying the app for real users.
