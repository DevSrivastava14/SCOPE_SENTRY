## Development Progress & Daily Roadmap

**Current status:** Day 3 completed
**Project phase:** Frontend-to-AI scope-analysis workflow implemented and verified; change ledger and client reply features are next.

This section is the source of truth for daily development progress. Update it at the end of each development day. Mark a task complete only after implementation and verification.

### Day 1 — Project Setup & Foundation

**Status: COMPLETED**

- [x] Created the ScopeSentry project directory.
- [x] Set up the Python virtual environment.
- [x] Created the FastAPI backend.
- [x] Added `GET /` as the root endpoint.
- [x] Added `GET /health` as the health-check endpoint.
- [x] Configured CORS for the local React frontend at `http://localhost:5173`.
- [x] Created the React + Vite frontend.
- [x] Started and verified the frontend development server.
- [x] Connected React to FastAPI using a health-check request.
- [x] Verified that the backend returns the expected health response.
- [x] Initialized Git and created the first local commit.
- [x] Established the initial project structure.

**Day 1 outcome:** The frontend and backend run locally and communicate successfully. The application currently contains only a basic connectivity test; scope analysis and the final product interface have not been implemented.

**Remaining repository setup:** Create the remote GitHub repository and push the local commits.

### Day 2 — AI Analysis Backend

**Goal:** Build the first working scope-creep analysis workflow.

- [x] Define the request and response formats for scope analysis.
- [x] Create a FastAPI endpoint for submitting the original agreement and new client request.
- [x] Configure the Groq API on the backend using the `openai/gpt-oss-120b` model.
- [x] Store the Groq API key in a backend `.env` file.
- [x] Add `.env` to `.gitignore` and provide a sanitized `.env.example`.
- [x] Implement the initial AI analysis service.
- [x] Return structured analysis results instead of unstructured text where practical.
- [x] Validate empty or invalid inputs.
- [x] Handle API failures, timeouts, and malformed AI responses.
- [x] Test the endpoint using FastAPI `/docs`.

**Completion criteria:** A valid request can be submitted to the backend and produces a structured analysis response, with errors handled appropriately.

**Day 2 outcome:** The backend now exposes `POST /analyze` with the existing Pydantic
request and response schemas. It uses Groq's OpenAI-compatible API, validates
supporting evidence against the supplied agreement and client request, and returns
safe errors for missing configuration, provider failures, timeouts, malformed output,
and invalid input. A live Groq inference request succeeded before this roadmap update.

**Day 2 verification:** No automated backend test suite exists yet. Focused mocked
checks passed for request validation, response parsing, unsupported evidence quotes,
missing `GROQ_API_KEY`, malformed model output, provider errors, timeout handling,
the existing root and health routes, and `/docs`. Python compilation and
`git diff --check` also passed.

### Day 3 — Frontend Analysis Experience

**Goal:** Allow a freelancer to use the core analysis workflow through the React interface.

- [x] Replace the temporary connectivity page with the first ScopeSentry interface.
- [x] Add an input area for the original agreement or scope of work.
- [x] Add an input area for the new client request.
- [x] Add an optional hourly-rate input.
- [x] Connect the form to the FastAPI analysis endpoint.
- [x] Show loading, success, and error states.
- [x] Display identified changes and their supporting text evidence.
- [x] Distinguish potentially out-of-scope changes from in-scope or unclear changes.
- [x] Make the results readable and easy to understand.

**Completion criteria:** A user can submit both texts in the browser and view the backend's analysis results.

**Day 3 outcome:** The temporary health-check page was replaced with the ScopeSentry
analysis interface. Freelancers can submit the original agreement and new client
request through controlled inputs, optionally provide an hourly rate, and receive
the structured analysis from the existing FastAPI `POST /analyze` endpoint. The
interface displays the AI summary, classified findings, supporting evidence,
uncertainty, and missing information without fabricating results or evidence.

**Day 3 verification:** The complete live frontend-to-backend-to-Groq analysis
workflow was successfully tested with a realistic example, and the returned
analysis appeared in the browser. The frontend CSS loading issue was fixed and
the intended styling was confirmed in the browser. Frontend lint and production
build checks passed, and `git diff --check` passed. Mobile responsiveness,
hourly-rate cost calculations, and additional test scenarios were not verified
as part of Day 3.

### Day 4 — Change Ledger & Client Reply

**Goal:** Make the analysis useful for real freelancer-client conversations.

- [ ] Present the identified changes in a clear change ledger.
- [ ] Show evidence from the supplied agreement and client request.
- [ ] Explain possible impacts on deliverables, effort, timeline, or cost when supported by the evidence.
- [ ] Avoid inventing contractual terms, prices, or estimates.
- [ ] Generate a professional, editable response the freelancer can send to the client.
- [ ] Handle ambiguous requests without presenting uncertain conclusions as facts.
- [ ] Test several realistic client-request scenarios.

**Completion criteria:** A freelancer can understand the flagged changes, review the supporting evidence, and edit a suggested client response.

### Day 5 — UI Polish, Testing & Documentation

**Goal:** Turn the working MVP into a presentable project.

- [ ] Improve the visual design and overall user experience.
- [ ] Ensure the interface works on common desktop and mobile screen sizes.
- [ ] Add appropriate empty, loading, and error states.
- [ ] Run frontend and backend checks.
- [ ] Verify the complete frontend-to-AI workflow.
- [ ] Review environment configuration and secret handling.
- [ ] Finalize the README, setup instructions, and API documentation.
- [ ] Add screenshots or a demo if available.
- [ ] Review deployment options and deploy if the application is stable.
- [ ] Review Hacktoberfest participation requirements before describing the project as eligible.

**Completion criteria:** The MVP works end to end, has been tested, and can be demonstrated with clear setup instructions.

### Day 6 — Buffer & Final Improvements (If Needed)

**Goal:** Address issues discovered during testing rather than adding unnecessary features.

- [ ] Fix confirmed bugs.
- [ ] Improve weak or confusing analysis results.
- [ ] Review performance, reliability, and error handling.
- [ ] Resolve remaining deployment or configuration issues.
- [ ] Update this roadmap to reflect actual progress.

This day is reserved for quality improvements. It does not require adding extra features if the MVP is already stable.

---

## Technical Stack

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI
- **AI provider:** Groq API using the OpenAI-compatible client and `openai/gpt-oss-120b`
- **Version control:** Git and GitHub

## Development Rules for GitHub Copilot

1. Read this progress tracker before starting a new task.
2. Work only on the current day's unfinished tasks unless explicitly instructed otherwise.
3. Make small, focused changes instead of attempting the entire day's work at once.
4. Inspect relevant files before editing them; preserve existing working functionality.
5. Do not recreate the frontend or backend if they already exist.
6. Keep the Groq API key on the backend. Never expose secrets in frontend code or commit them to Git.
7. Do not add a database, authentication, payments, or unrelated features unless explicitly requested.
8. Verify changes using appropriate tests or manual checks.
9. Report which files changed, what was implemented, and which checks actually passed.
10. Do not mark tasks complete based solely on writing code. Confirm that the functionality works.
11. At the end of each day, update the checkboxes and daily status in this README.
12. If a task is blocked, explain the blocker and propose the smallest next step instead of repeatedly retrying expensive operations.

## Immediate Next Steps

1. Present the identified changes in a clear change ledger.
2. Show agreement and client-request evidence in the change ledger.
3. Explain supported impacts on deliverables, effort, timeline, or cost.
4. Generate a professional, editable response the freelancer can send to the client.

### Backend provider configuration

Create `backend/.env` locally and set:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

The backend uses Groq's OpenAI-compatible endpoint at
`https://api.groq.com/openai/v1`. Keep `backend/.env` local and never commit the
API key.
