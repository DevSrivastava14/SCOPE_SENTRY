import { useState } from "react";
import "./App.css";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");
const API_URL = `${API_BASE_URL}/analyze`;

const initialForm = {
  originalAgreement: "",
  newClientRequest: "",
  hourlyRate: "",
};

function classificationLabel(classification) {
  return {
    in_scope: "In scope",
    out_of_scope: "Potentially out of scope",
    unclear: "Needs clarification",
  }[classification] || "Unclear";
}

function hasUsableEstimate(estimate) {
  return estimate && (
    Number.isFinite(estimate.minimum) ||
    Number.isFinite(estimate.maximum)
  );
}

function formatEstimate(estimate) {
  const minimum = Number.isFinite(estimate.minimum) ? estimate.minimum : "—";
  const maximum = Number.isFinite(estimate.maximum) ? estimate.maximum : "—";
  return minimum === maximum ? `${minimum} hours` : `${minimum}–${maximum} hours`;
}

function App() {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [editableReply, setEditableReply] = useState("");
  const [copyStatus, setCopyStatus] = useState("idle");

  const updateField = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const originalAgreement = form.originalAgreement.trim();
    const newClientRequest = form.newClientRequest.trim();

    if (!originalAgreement || !newClientRequest) {
      setError("Add both the original agreement and the new client request.");
      setStatus("error");
      return;
    }

    if (form.hourlyRate !== "" && Number(form.hourlyRate) < 0) {
      setError("Hourly rate cannot be negative.");
      setStatus("error");
      return;
    }

    const requestBody = {
      original_agreement: originalAgreement,
      new_client_request: newClientRequest,
    };
    if (form.hourlyRate !== "") {
      requestBody.hourly_rate = Number(form.hourlyRate);
    }

    setStatus("loading");
    setError("");
    setAnalysis(null);
    setEditableReply("");
    setCopyStatus("idle");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "The analysis could not be completed. Please try again.",
        );
      }

      setAnalysis(data);
      setEditableReply(data.suggested_client_reply);
      setStatus("success");
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Could not connect to the ScopeSentry API.",
      );
      setStatus("error");
    }
  };

  const findings = analysis?.findings ?? [];
  const missingInformation = analysis?.missing_information ?? [];

  const copyReply = async () => {
    if (!editableReply.trim()) {
      setCopyStatus("error");
      return;
    }

    try {
      await navigator.clipboard.writeText(editableReply);
      setCopyStatus("copied");
    } catch {
      setCopyStatus("error");
    }
  };

  return (
    <main className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="ScopeSentry home">
          <span className="brand-mark" aria-hidden="true">S</span>
          <span>ScopeSentry</span>
        </a>
        <span className="header-note">Clarity for client changes</span>
      </header>

      <section className="intro">
        <p className="eyebrow">Scope analysis for freelancers</p>
        <h1>Know what changed before you say yes.</h1>
        <p className="intro-copy">
          Compare the agreement with a new client request and get a grounded,
          easy-to-review breakdown of the differences.
        </p>
      </section>

      <form className="analysis-form" onSubmit={handleSubmit} noValidate>
        <div className="form-heading">
          <div>
            <p className="eyebrow">Start an analysis</p>
            <h2>Bring your project context</h2>
          </div>
          <span className="required-note">* Required</span>
        </div>

        <div className="text-inputs">
          <label className="field">
            <span>Original agreement <b aria-hidden="true">*</b></span>
            <small>Paste the scope of work, proposal, or agreed deliverables.</small>
            <textarea
              name="originalAgreement"
              value={form.originalAgreement}
              onChange={updateField}
              placeholder="Example: The project includes a five-page marketing website..."
              required
              rows="9"
            />
          </label>
          <label className="field">
            <span>New client request <b aria-hidden="true">*</b></span>
            <small>Describe what the client is asking to add or change.</small>
            <textarea
              name="newClientRequest"
              value={form.newClientRequest}
              onChange={updateField}
              placeholder="Example: Could we also add a customer dashboard..."
              required
              rows="9"
            />
          </label>
        </div>

        <div className="form-footer">
          <label className="rate-field">
            <span>Hourly rate <em>(optional)</em></span>
            <div className="rate-input">
              <span aria-hidden="true">$</span>
              <input
                name="hourlyRate"
                value={form.hourlyRate}
                onChange={updateField}
                type="number"
                min="0"
                step="0.01"
                placeholder="0.00"
                inputMode="decimal"
              />
            </div>
          </label>
          <button className="analyze-button" type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Analyzing..." : "Analyze scope"}
            {status !== "loading" && <span aria-hidden="true">→</span>}
          </button>
        </div>
      </form>

      {status === "error" && (
        <div className="status-message error-message" role="alert">
          <strong>Analysis not completed</strong>
          <span>{error}</span>
        </div>
      )}

      {status === "success" && analysis && (
        <section className="results" aria-live="polite">
          <div className="results-header">
            <div>
              <p className="eyebrow">Analysis complete</p>
              <h2>Here&apos;s what ScopeSentry found</h2>
            </div>
            <span className="result-count">
              {findings.length} {findings.length === 1 ? "change" : "changes"}
            </span>
          </div>

          <div className="summary-card">
            <span className="summary-label">Overall summary</span>
            <p>{analysis.overall_summary}</p>
          </div>

          {findings.length > 0 ? (
            <div className="change-ledger">
              <div className="ledger-heading">
                <span className="detail-label">Change ledger</span>
                <span className="ledger-note">Review each change before responding</span>
              </div>
              <div className="findings-list">
              {findings.map((finding, index) => (
                <article className="finding-card" key={`${finding.change_description}-${index}`}>
                  <div className="finding-header">
                    <div className="finding-topline">
                      <span className="finding-number">Change {String(index + 1).padStart(2, "0")}</span>
                      <span className={`classification ${finding.classification}`}>
                        <span className="classification-dot" aria-hidden="true" />
                        {classificationLabel(finding.classification)}
                      </span>
                    </div>
                    <h3>{finding.change_description}</h3>
                  </div>

                  <div className="finding-details">
                    <div className="finding-explanation-block">
                      <span className="detail-label">Why this was flagged</span>
                      <p className="finding-explanation">{finding.explanation}</p>
                    </div>

                    <div className="evidence-block">
                      <span className="detail-label">Supporting evidence</span>
                      <p className="evidence-note">Quoted from the supplied agreement or client request.</p>
                    </div>
                    <div className="quotations">
                      {(finding.supporting_evidence ?? []).map((evidence, evidenceIndex) => (
                        <blockquote key={`${evidence}-${evidenceIndex}`}>{evidence}</blockquote>
                      ))}
                    </div>

                    {finding.uncertainty && (
                      <div className="uncertainty">
                        <span className="detail-label">Uncertainty to review</span>
                        <p>{finding.uncertainty}</p>
                      </div>
                    )}

                    {hasUsableEstimate(finding.estimated_extra_hours) && (
                      <div className="estimate">
                        <span className="detail-label">Estimated extra effort</span>
                        <p>{formatEstimate(finding.estimated_extra_hours)}</p>
                        {(finding.estimated_extra_hours.assumptions ?? []).length > 0 && (
                          <ul>
                            {finding.estimated_extra_hours.assumptions.map((assumption, assumptionIndex) => (
                              <li key={`${assumption}-${assumptionIndex}`}>{assumption}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}
                  </div>
                </article>
              ))}
              </div>
            </div>
          ) : (
            <div className="empty-results">
              <span aria-hidden="true">✓</span>
              <p>No specific changes were identified in the supplied text.</p>
            </div>
          )}

          {missingInformation.length > 0 && (
            <div className="missing-info">
              <span className="detail-label">Information to clarify</span>
              <ul>
                {missingInformation.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
              </ul>
            </div>
          )}

          <div className="client-reply">
            <div className="reply-heading">
              <div>
                <span className="detail-label">Suggested client reply</span>
                <p>Edit this grounded draft before sending it to the client.</p>
              </div>
              <button className="copy-button" type="button" onClick={copyReply}>
                {copyStatus === "copied" ? "Copied" : "Copy reply"}
              </button>
            </div>
            <textarea
              className="reply-input"
              value={editableReply}
              onChange={(event) => {
                setEditableReply(event.target.value);
                setCopyStatus("idle");
              }}
              aria-label="Suggested client reply"
              rows="9"
            />
            {copyStatus === "copied" && (
              <p className="copy-feedback success-feedback" role="status">
                Reply copied to your clipboard.
              </p>
            )}
            {copyStatus === "error" && (
              <p className="copy-feedback error-feedback" role="alert">
                The reply could not be copied. Select the text and copy it manually.
              </p>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
