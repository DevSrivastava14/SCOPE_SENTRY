# 🛡️ ScopeSentry

### Protect your time. Clarify the scope. Get paid for extra work.

**ScopeSentry is an AI-powered scope analysis tool that helps freelancers identify scope creep before agreeing to additional client work.**

It compares an original agreement or statement of work against a new client request, identifies potential changes in project scope, provides exact supporting evidence, highlights missing information, and generates an editable response to help freelancers communicate professionally.

Instead of relying on vague AI summaries, ScopeSentry emphasizes **evidence-grounded analysis, structured findings, and transparent uncertainty.**

---

## ✨ Why ScopeSentry?

Scope creep is one of the most common challenges freelancers face.

A project begins with an agreed set of deliverables. Gradually, clients introduce additional requirements, features, revisions, and responsibilities that were never explicitly included in the original agreement.

These changes can result in:
- Unpaid additional work.
- Unclear project expectations.
- Unexpected deadlines.
- Disagreements between freelancers and clients.
- Lost time and reduced profitability.

Freelancers need a way to distinguish between what was originally agreed upon and what is being requested now.

**ScopeSentry brings clarity to that process.**

## 🚀 Features

| Feature | Description |
|---|---|
| 📄 Agreement Analysis | Compare an original agreement or scope of work with a new client request. |
| 🔍 Scope Classification | Classify findings as `in_scope`, `out_of_scope`, or `needs_clarification`. |
| 📌 Evidence-Grounded Findings | Display exact supporting excerpts from the supplied agreement and request. |
| 🧠 AI Explanations | Explain why a particular change may affect the original scope. |
| ⚖️ Uncertainty Assessment | Make uncertainty visible instead of presenting AI conclusions as absolute facts. |
| ❓ Missing Information | Identify details that should be clarified before accepting additional work. |
| ⏱️ Effort Estimation | Display estimated additional hours when usable estimates and assumptions are available. |
| ✉️ Suggested Client Reply | Generate a context-aware, editable response for communicating scope changes. |
| 📋 Copy to Clipboard | Copy the edited client response with a manual-copy fallback. |
| 🔒 Privacy-Safe Diagnostics | Avoid logging agreement text, client requests, model output, replies, or API credentials in diagnostic output. |
| 🧪 Regression Testing | Validate backend behavior using deterministic tests and mocked AI provider responses. |

## ⚙️ How It Works

ScopeSentry follows a straightforward workflow:

1. **Provide the original agreement:** Paste the original contract excerpt, project requirements, or statement of work.
2. **Enter the new request:** Provide the client's additional or modified requirements.
3. **Add an hourly rate (optional):** Supply a rate for future-compatible effort estimation.
4. **Analyze the changes:** The backend sends the supplied information to the configured AI provider.
5. **Review the findings:** Examine classifications, explanations, supporting evidence, uncertainty, and missing information.
6. **Review the effort estimate:** Inspect additional-hour estimates and their assumptions when available.
7. **Prepare your response:** Edit the AI-generated client reply and copy it when ready.

### Example

**Original agreement:**
> The project includes a five-page website.

**New client request:**
> Please add a customer dashboard.

**ScopeSentry identifies:**

| Field | Analysis |
|---|---|
| Change | Add a customer dashboard |
| Classification | `out_of_scope` |
| Explanation | The request introduces a deliverable not described in the supplied agreement excerpt. |
| Supporting evidence | "Please add a customer dashboard." |
| Uncertainty | The agreement excerpt may not contain every project detail. |

The result is not just an AI-generated opinion. It is a structured finding that can be reviewed against the actual supplied text.

*The example is illustrative; real classifications depend on the submitted documents and their context.*

## 🏗️ Architecture

ScopeSentry uses a React frontend, a FastAPI backend, structured Pydantic validation, and Groq-hosted AI inference.

```text
                 ┌─────────────────────────┐
                 │       Freelancer        │
                 │                         │
                 │ Original Agreement      │
                 │ New Client Request      │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     React Frontend      │
                 │       React 19          │
                 │                         │
                 │ Input & Results UI      │
                 │ Editable Client Reply   │
                 └────────────┬────────────┘
                              │
                         POST /analyze
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      FastAPI Backend    │
                 │                         │
                 │ Request Validation      │
                 │ Analysis Service        │
                 │ Response Validation     │
                 │ Evidence Verification   │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      Groq API           │
                 │                         │
                 │ openai/gpt-oss-120b     │
                 └────────────┬────────────┘
                              │
                       Structured Output
                              │
                              ▼
                 ┌─────────────────────────┐
                 │ Validated Findings      │
                 │ Evidence & Explanations │
                 │ Suggested Client Reply  │
                 └─────────────────────────┘
```

### Evidence Validation

A key design decision in ScopeSentry is that AI-generated evidence must be verifiable.

The backend validates model-provided supporting evidence against the submitted agreement and client request. Evidence must be a contiguous, character-for-character substring of the original supplied text.

This helps prevent fabricated or paraphrased quotations from being presented as direct supporting evidence.

Pydantic models also validate structured request and response data before it is returned to the frontend.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 |
| Frontend Tooling | Vite |
| Backend | Python, FastAPI |
| Data Validation | Pydantic 2 |
| AI Provider | Groq |
| AI Model | `openai/gpt-oss-120b` |
| Provider Integration | OpenAI Python Client |
| API Communication | HTTP / JSON |
| Testing | Pytest |
| Environment Management | Python Virtual Environment |

### Why This Stack?

- **React + Vite:** Provides a responsive frontend and fast development workflow.
- **FastAPI:** Handles asynchronous API operations and connects the frontend with the analysis service.
- **Pydantic:** Enforces structured input and output validation.
- **Groq:** Provides access to hosted AI inference through an OpenAI-compatible API.
- **Pytest:** Supports deterministic backend regression testing without depending on live AI responses.

## 📂 Repository Structure

```text
ScopeSentry/
│
├── backend/
│   ├── analysis_service.py
│   ├── main.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── ...
│
└── README.md
```

## 💻 Getting Started

Follow these instructions to run ScopeSentry locally.

### Prerequisites

- Python 3.13 (recommended for the verified environment).
- Node.js and npm.
- A Groq API key.
- Git.

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ScopeSentry
```

Replace the repository URL with your GitHub repository URL.

### 2. Set Up the Backend

Navigate to the backend directory:

**Windows:**

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `backend/.env.example` to `backend/.env`.

Configure your credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

**Important:** Never commit your actual API key or expose it in frontend code.

### 4. Configure the Frontend

Copy `frontend/.env.example` to `frontend/.env`.

Set the backend URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The backend CORS configuration explicitly supports the local frontend origin:

```text
http://localhost:5173
```

### 5. Start the Backend

Open Terminal 1.

**Windows:**

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

**macOS / Linux:**

```bash
cd backend
./.venv/bin/python -m uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 6. Start the Frontend

Open Terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Open the URL displayed by Vite, normally:

```text
http://localhost:5173
```

ScopeSentry is now ready for local use.

## 🔌 API Documentation

ScopeSentry exposes the following backend endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns basic API information. |
| GET | `/health` | Checks backend health. |
| POST | `/analyze` | Analyzes an original agreement against a new client request. |

### POST `/analyze`

**Request Body:**

```json
{
  "original_agreement": "The project includes a five-page website.",
  "new_client_request": "Please add a customer dashboard.",
  "hourly_rate": 75
}
```

`hourly_rate` is optional and must be zero or greater. Both text fields must contain nonblank text.

**Response Structure:**

```json
{
  "overall_summary": "The request introduces a dashboard that is not described in the supplied scope.",
  "suggested_client_reply": "Thanks for the request. Let us confirm the updated scope before proceeding.",
  "findings": [
    {
      "change_description": "Add a customer dashboard",
      "classification": "out_of_scope",
      "supporting_evidence": [
        "Please add a customer dashboard."
      ],
      "explanation": "The request describes a deliverable not included in the supplied agreement excerpt.",
      "uncertainty": "The agreement excerpt may not contain every project detail.",
      "estimated_extra_hours": null
    }
  ],
  "missing_information": []
}
```

The example demonstrates the response structure. Actual findings and estimates depend on the supplied information and model output.

### Finding Classifications

| Classification | Meaning |
|---|---|
| `in_scope` | The requested change appears consistent with the supplied agreement. |
| `out_of_scope` | The requested change appears to introduce work beyond the supplied agreement. |
| `needs_clarification` | More information is needed before determining whether the change falls within the original scope. |

## 🧪 Testing & Quality Checks

ScopeSentry includes a backend regression suite designed to verify application behavior without making live Groq API requests.

### Backend Tests

From the `backend` directory:

**Windows:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

**macOS / Linux:**

```bash
./.venv/bin/python -m pytest tests -q
```

**Verified result:** 31 passing tests.

The tests use mocked provider behavior to keep the regression suite deterministic.

### Frontend Checks

From the `frontend` directory:

```bash
npm run lint
npm run build
```

### Python Compilation

From the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m py_compile analysis_service.py schemas.py main.py tests\test_backend.py
```

### Git Diff Validation

From the repository root:

```bash
git diff --check
```

## 🔐 Privacy & Security

ScopeSentry takes care to avoid exposing sensitive information through diagnostic logging and frontend configuration.

- API credentials remain in the backend environment.
- API keys are never intended to be exposed in browser code.
- Diagnostic output avoids logging agreement text, client requests, raw model responses, generated replies, and API keys.
- Model-provided evidence is checked against the actual submitted text.
- Structured inputs and outputs are validated before being processed or displayed.

**Important privacy consideration:** ScopeSentry uses Groq-hosted inference. The agreement text and client request submitted for analysis are sent to the configured Groq API. This is not a fully local or offline AI application. Review the provider's applicable data-handling policies before submitting confidential client information.

## ⚠️ Limitations & Responsible Use

ScopeSentry is an analysis assistant, not a replacement for professional judgment.

- AI classifications are suggestions, not definitive contractual conclusions.
- An agreement excerpt may not contain the complete project scope.
- Effort estimates are approximate and may be omitted when sufficient information is unavailable.
- Evidence validation verifies quotations, but does not guarantee that the AI interpretation is correct.
- Users should review explanations, uncertainty, and missing information before making decisions.
- ScopeSentry does not provide legal advice.
- ScopeSentry does not send client messages or provide email integration.
- No production deployment or hosting configuration is included in this repository.

Always review the original agreement and consult a qualified professional when legal or contractual interpretation is required.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes.
4. Add or update deterministic tests for behavior changes.
5. Run the backend regression suite and frontend lint/build checks.
6. Run Python compilation and `git diff --check`.
7. Submit a pull request explaining the changes and their impact.

### Contribution Guidelines

- Keep changes focused and maintainable.
- Avoid introducing unnecessary dependencies.
- Never commit API keys, credentials, or confidential client information.
- Preserve evidence validation and structured response behavior.
- Document user-visible changes and known limitations.

## 🛡️ Security Reporting

If you discover a security vulnerability, avoid publishing sensitive details in a public issue.

Use the repository's available private GitHub security reporting process, or contact the maintainer directly if private reporting is not enabled.

## 🏆 Hacktoberfest 2026

ScopeSentry was developed in the context of the DEV/Hacktoberfest 2026 open-source challenge.

The project explores how open-source AI can solve a practical problem faced by independent professionals.

Its central idea is simple:

**AI should not just generate an answer. It should provide evidence that people can inspect, question, and use to make better decisions.**

ScopeSentry demonstrates this through structured AI analysis, exact evidence verification, transparent uncertainty, and human-reviewed communication.

## 🙏 Acknowledgements

Built with the support of the following open-source technologies and services:

- [React](https://react.dev/) — Frontend library.
- [Vite](https://vite.dev/) — Frontend development tooling.
- [FastAPI](https://fastapi.tiangolo.com/) — Python API framework.
- [Pydantic](https://docs.pydantic.dev/) — Data validation.
- [Groq](https://groq.com/) — AI inference provider.
- [OpenAI Python SDK](https://github.com/openai/openai-python) — Provider integration.
- [Pytest](https://pytest.org/) — Backend testing framework.

---

<p align="center">
  <b>Built to help freelancers protect their time, clarify expectations, and work with confidence.</b>
  <br/>
  ⭐ If you find ScopeSentry useful, consider starring the repository!
</p>