# ScopeSentry

## Protect your time. Clarify the scope. Get paid for extra work.

ScopeSentry helps freelancers review potential scope creep before agreeing to
new client work. It compares an original agreement or scope of work with a new
client request and presents an evidence-grounded analysis that is easier to
review and discuss.

## Features

- Compare an original agreement with a new client request.
- Classify individual findings as **in scope**, **potentially out of scope**, or
  **needs clarification**.
- Show the change description, explanation, uncertainty, and exact supporting
  evidence for each finding.
- Validate model-provided evidence as a contiguous, character-for-character
  substring of the supplied agreement or request.
- Show missing information that should be clarified.
- Display extra-hour estimates only when usable values are returned, together
  with their assumptions.
- Generate a grounded, editable suggested client reply.
- Copy the edited reply to the clipboard, with a manual-copy fallback message
  when clipboard access fails.
- Provide privacy-safe diagnostics for malformed provider responses without
  logging user text, model output, replies, or API keys.

## How it works

1. Paste the original agreement or scope of work.
2. Paste the client's new or changed request.
3. Optionally enter an hourly rate for future-compatible request handling.
4. Submit the analysis.
5. Review the summary, change ledger, exact evidence, uncertainty, missing
   information, and any supported effort estimate.
6. Edit the suggested reply before sending it yourself.

ScopeSentry does not send messages to clients or provide email integration.

## Screenshots and demo

This repository does not currently include a verified screenshot, hosted demo,
or deployed application URL. The application can be run locally using the
instructions below.

## Technology and architecture

- **Frontend:** React 19 with Vite
- **Backend:** Python with FastAPI
- **Validation:** Pydantic 2 request and response models
- **AI provider:** Groq through its OpenAI-compatible API
- **Model:** `openai/gpt-oss-120b` by default
- **Frontend/backend flow:** The React app sends JSON to FastAPI `POST /analyze`.
  The backend calls Groq, validates the structured response and evidence, then
  returns the response to the browser.

Relevant directories:

```text
backend/
  analysis_service.py
  main.py
  schemas.py
  requirements.txt
  tests/
frontend/
  src/
  package.json
  .env.example
```

## Prerequisites

- Windows, macOS, or Linux
- Python 3.13 recommended for the verified local environment
- Node.js and npm
- A Groq API key for live analysis requests

## Installation

### Backend

From the repository root on Windows:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
cd backend
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### Environment variables

Copy `backend/.env.example` to `backend/.env` and set your local provider
credential:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit `backend/.env` or place the API key in frontend code.

The frontend API base defaults to `http://localhost:8000`. To override it,
copy `frontend/.env.example` to `frontend/.env` and set:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The backend CORS configuration explicitly supports the local frontend origin
`http://localhost:5173`.

## Running locally

Use two terminals.

### Terminal 1: backend

Windows:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

macOS or Linux:

```bash
cd backend
./.venv/bin/python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`.

### Terminal 2: frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally
`http://localhost:5173`.

## API overview

### `GET /`

Returns basic API information:

```json
{
  "message": "Welcome to ScopeSentry API",
  "docs": "/docs"
}
```

### `GET /health`

Returns the service health response:

```json
{
  "status": "ok",
  "application": "ScopeSentry"
}
```

### `POST /analyze`

Request:

```json
{
  "original_agreement": "The project includes a five-page website.",
  "new_client_request": "Please add a customer dashboard.",
  "hourly_rate": 75
}
```

`hourly_rate` is optional and must be zero or greater. The two text fields must
not be blank.

The response contains `overall_summary`, `suggested_client_reply`,
`missing_information`, and a `findings` array. Each finding contains
`change_description`, `classification`, `supporting_evidence`, `explanation`,
`uncertainty`, and an optional `estimated_extra_hours` object:

```json
{
  "overall_summary": "The request introduces a dashboard that is not described in the supplied scope.",
  "suggested_client_reply": "Thanks for the request. Let us confirm the updated scope before proceeding.",
  "findings": [
    {
      "change_description": "Add a customer dashboard",
      "classification": "out_of_scope",
      "supporting_evidence": ["Please add a customer dashboard."],
      "explanation": "The request describes a deliverable not included in the supplied agreement excerpt.",
      "uncertainty": "The agreement excerpt may not contain every project detail.",
      "estimated_extra_hours": null
    }
  ],
  "missing_information": []
}
```

The evidence in this example is illustrative request data; actual evidence must
be copied exactly from the submitted text. Interactive API documentation is
available at `http://localhost:8000/docs` while the backend is running.

## Tests and quality checks

Run the backend regression suite from `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Run frontend checks from `frontend`:

```powershell
npm run lint
npm run build
```

Compile the relevant backend and test files:

```powershell
.\.venv\Scripts\python.exe -m py_compile analysis_service.py schemas.py main.py tests\test_backend.py
```

Check the Git diff for whitespace errors from the repository root:

```powershell
git diff --check
```

The verified local regression suite contains 31 passing tests. It uses mocked
provider behavior and does not require live Groq requests.

## Limitations and responsible use

- Scope classifications and effort estimates are analysis aids, not definitive
  contractual conclusions.
- Estimates are approximate and may be absent when the supplied text does not
  support them.
- Review the original agreement, client request, evidence, uncertainty, and
  missing information before making a business decision.
- ScopeSentry does not provide legal advice. Consult a qualified professional
  for legal or contractual questions.
- The model can still be wrong or incomplete. Strict evidence validation helps
  prevent unsupported quotations but does not guarantee correct interpretation.
- No deployment or production hosting configuration is included in this
  repository.

## Contributing

Small, focused contributions are welcome:

1. Open an issue describing the problem or proposed improvement.
2. Keep changes scoped to the relevant frontend, backend, tests, or
   documentation.
3. Do not add secrets, credentials, generated build output, or local
   environments.
4. Add or update deterministic tests for behavior changes.
5. Run the backend tests, frontend lint/build, Python compilation, and
   `git diff --check` before opening a pull request.
6. Explain user-visible behavior changes and any limitations in the pull
   request description.

## Security

Keep `GROQ_API_KEY` only in the ignored `backend/.env` file. Use the sanitized
`.env.example` files for setup documentation. Do not include API keys, client
agreements, client requests, raw model output, or other sensitive data in
issues, logs, commits, or pull requests.

For a suspected vulnerability, avoid posting sensitive details publicly. Open
a private security report through the repository's available GitHub security
contact process, or contact the maintainer directly if private reporting is
not enabled.

## Hacktoberfest and DEV challenge context

ScopeSentry was developed as an open-source project for a DEV/Hacktoberfest
challenge context. The repository demonstrates an evidence-first workflow for
reviewing freelance scope changes with a React interface, FastAPI service,
structured validation, and mocked regression tests. Eligibility and submission
requirements should be confirmed against the current DEV/Hacktoberfest rules
before submission.

## Acknowledgements

- React and Vite for the frontend tooling.
- FastAPI and Pydantic for the API and validation layer.
- Groq for the OpenAI-compatible model API.
- The OpenAI Python client for the provider integration.
