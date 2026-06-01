import { useState } from "react";
import type {
  AnswerQualityIntent,
  EvaluationResponse,
  SourcePreferences,
} from "../../types/evaluation";
import { DIMENSION_LABELS } from "../../types/evaluation";
import { AttributionChains } from "../attribution/AttributionChains";
import { ReasoningPath } from "../reasoning/ReasoningPath";

interface EvaluationPanelProps {
  claimVerificationEnabled: boolean;
  onClaimVerificationEnabledChange: (value: boolean) => void;
  sourcePreferences: SourcePreferences;
  onSourcePreferencesChange: (prefs: SourcePreferences) => void;
  answerQualityIntent: AnswerQualityIntent;
  onAnswerQualityIntentChange: (intent: AnswerQualityIntent) => void;
  regenerate: boolean;
  onRegenerateChange: (value: boolean) => void;
  onEvaluate: () => void;
  loading: boolean;
  canEvaluate: boolean;
  result: EvaluationResponse | null;
  error: string | null;
}

type AccordionSection =
  | "claim_verification"
  | "source_transparency"
  | "logic_reasoning"
  | "missing_factors"
  | "improve_answer_quality";

const SOURCE_KEYS: (keyof SourcePreferences)[] = [
  "memory",
  "user_context",
  "web",
  "research",
  "company",
  "internal",
];

const SOURCE_LABELS: Record<keyof SourcePreferences, string> = {
  memory: "Memory",
  user_context: "User-Provided Context",
  web: "Web Sources",
  research: "Research & Reports",
  company: "Company Information",
  internal: "Internal Knowledge",
};

export function EvaluationPanel({
  claimVerificationEnabled,
  onClaimVerificationEnabledChange,
  sourcePreferences,
  onSourcePreferencesChange,
  answerQualityIntent,
  onAnswerQualityIntentChange,
  regenerate,
  onRegenerateChange,
  onEvaluate,
  loading,
  canEvaluate,
  result,
  error,
}: EvaluationPanelProps) {
  const [isPanelExpanded, setIsPanelExpanded] = useState(true);
  const [sourceUrl, setSourceUrl] = useState("");
  const [expandedSections, setExpandedSections] = useState<Set<AccordionSection>>(
    new Set([
      "claim_verification",
      "source_transparency",
      "logic_reasoning",
      "missing_factors",
      "improve_answer_quality",
    ])
  );

  const updateIntent = (field: keyof AnswerQualityIntent, value: string) => {
    onAnswerQualityIntentChange({ ...answerQualityIntent, [field]: value });
  };

  const toggleSection = (section: AccordionSection) => {
    const next = new Set(expandedSections);
    if (next.has(section)) {
      next.delete(section);
    } else {
      next.add(section);
    }
    setExpandedSections(next);
  };

  const statusBadge = result
    ? result.status === "completed"
      ? "Ready"
      : result.status === "processing"
      ? "Processing"
      : "Error"
    : "Waiting";

  const statusColor = result
    ? result.status === "completed"
      ? "bg-green-100 text-green-700"
      : result.status === "processing"
      ? "bg-blue-100 text-blue-700"
      : "bg-red-100 text-red-700"
    : "bg-slate-100 text-slate-600";

  return (
    <aside 
      className={`flex flex-col border-l border-slate-200 bg-white transition-all duration-300 overflow-hidden ${
        isPanelExpanded ? 'w-[45%] min-w-[400px]' : 'w-16 min-w-[64px]'
      }`}
    >
      {/* Header */}
      <header className={`border-b border-slate-200 ${isPanelExpanded ? 'px-5 py-4' : 'px-2 py-3'}`}>
        <button
          onClick={() => setIsPanelExpanded(!isPanelExpanded)}
          className="flex w-full items-center justify-between"
        >
          {isPanelExpanded ? (
            <>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Evaluation</h2>
                <p className="mt-1 text-xs text-slate-500">All 5 dimensions</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColor}`}>
                  {statusBadge}
                </span>
                <span className="text-slate-400 transition-transform duration-200" style={{ transform: 'rotate(0deg)' }}>
                  ▼
                </span>
              </div>
            </>
          ) : (
            <div className="flex w-full flex-col items-center justify-center gap-1">
              <span className="text-xs font-semibold text-slate-700 whitespace-nowrap">Evaluation</span>
              <span className="text-slate-400 text-sm">▶</span>
            </div>
          )}
        </button>
      </header>

      {/* Content */}
      {isPanelExpanded && (
        <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-5 py-4">
        {/* Evaluate Button */}
        <button
          type="button"
          onClick={onEvaluate}
          disabled={loading || !canEvaluate}
          className="rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Evaluating…" : result ? "Re-evaluate" : "Evaluate response"}
        </button>

        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={regenerate}
            onChange={(e) => onRegenerateChange(e.target.checked)}
          />
          Generate improved answer
        </label>

        {error && (
          <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
        )}

        {/* Section 1: Claim Verification */}
        <AccordionItem
          title={DIMENSION_LABELS.claim_verification}
          isExpanded={expandedSections.has("claim_verification")}
          onToggle={() => toggleSection("claim_verification")}
        >
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={claimVerificationEnabled}
              onChange={(e) => onClaimVerificationEnabledChange(e.target.checked)}
            />
            Enable claim verification
          </label>
          <p className="mt-2 text-xs text-slate-500">
            {claimVerificationEnabled
              ? "After evaluate: green / yellow / red highlights on the response."
              : "Highlights are hidden until this is enabled."}
          </p>
          {result && claimVerificationEnabled && result.evaluation.claims.length > 0 && (
            <ul className="mt-3 space-y-2">
              {result.evaluation.claims.map((c) => (
                <li key={c.claim_id} className="rounded-md bg-slate-50 p-2 text-sm">
                  <StatusBadge status={c.status} />
                  <span className="ml-2 font-mono text-xs text-slate-600">{c.claim_id}</span>
                  {c.verification_note && (
                    <p className="mt-1 text-xs text-slate-600">{c.verification_note}</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </AccordionItem>

        {/* Section 2: Source Transparency */}
        <AccordionItem
          title={DIMENSION_LABELS.source_transparency}
          isExpanded={expandedSections.has("source_transparency")}
          onToggle={() => toggleSection("source_transparency")}
        >
          <div className="space-y-1">
            {SOURCE_KEYS.map((key) => (
              <label key={key} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={sourcePreferences[key]}
                  onChange={(e) =>
                    onSourcePreferencesChange({
                      ...sourcePreferences,
                      [key]: e.target.checked,
                    })
                  }
                />
                {SOURCE_LABELS[key]}
              </label>
            ))}
          </div>

          {/* Add Own URL */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-700">
              Add your own source URL
            </label>
            <div className="mt-2 flex gap-2">
              <input
                type="url"
                placeholder="https://example.com/article"
                value={sourceUrl}
                onChange={(e) => setSourceUrl(e.target.value)}
                className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
              <button
                type="button"
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                onClick={() => {
                  if (sourceUrl.trim()) {
                    // TODO: Add URL to sources
                    setSourceUrl("");
                  }
                }}
              >
                Add
              </button>
            </div>
          </div>

          {/* Choose Files */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-700">
              Upload files (.txt, .md, .pdf)
            </label>
            <input
              type="file"
              multiple
              accept=".txt,.md,.pdf"
              className="mt-2 block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
              onChange={(e) => {
                if (e.target.files) {
                  // TODO: Handle file upload
                }
              }}
            />
          </div>

          <AttributionChains attribution={result?.attribution ?? null} />
        </AccordionItem>

        {/* Section 3: Logic & Reasoning */}
        <AccordionItem
          title={DIMENSION_LABELS.logic_reasoning}
          isExpanded={expandedSections.has("logic_reasoning")}
          onToggle={() => toggleSection("logic_reasoning")}
        >
          {result ? (
            <ReasoningPath logic={result.evaluation.logic} />
          ) : (
            <p className="text-xs text-slate-500">
              Run evaluate — click ▸ on each step to expand evidence.
            </p>
          )}
        </AccordionItem>

        {/* Section 4: Missing Factors */}
        <AccordionItem
          title={DIMENSION_LABELS.missing_factors}
          isExpanded={expandedSections.has("missing_factors")}
          onToggle={() => toggleSection("missing_factors")}
        >
          {result?.evaluation.missing_factors.length ? (
            <ul className="space-y-3">
              {result.evaluation.missing_factors.map((mf) => (
                <li key={mf.heading} className="flex gap-2">
                  <span className="text-amber-500">⚠️</span>
                  <div>
                    <p className="text-sm font-medium text-amber-900">{mf.heading}</p>
                    <p className="text-sm text-slate-600 line-clamp-2">{mf.summary}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-500">Compact gaps appear after evaluate.</p>
          )}
        </AccordionItem>

        {/* Section 5: Improve Answer Quality */}
        <AccordionItem
          title={DIMENSION_LABELS.improve_answer_quality}
          isExpanded={expandedSections.has("improve_answer_quality")}
          onToggle={() => toggleSection("improve_answer_quality")}
        >
          <div className="space-y-2">
            <IntentField
              label="What are you trying to decide or understand?"
              value={answerQualityIntent.user_intent ?? ""}
              onChange={(v) => updateIntent("user_intent", v)}
            />
            <IntentField
              label="Expertise level"
              value={answerQualityIntent.expertise_level ?? ""}
              placeholder="beginner, intermediate, expert"
              onChange={(v) => updateIntent("expertise_level", v)}
            />
            <IntentField
              label="What outcome do you need?"
              value={answerQualityIntent.user_goal ?? ""}
              onChange={(v) => updateIntent("user_goal", v)}
            />
            <IntentField
              label="Constraints or expectations"
              value={answerQualityIntent.constraints_or_expectations ?? ""}
              onChange={(v) => updateIntent("constraints_or_expectations", v)}
            />
            <IntentField
              label="What should a good answer look like?"
              value={answerQualityIntent.good_answer_looks_like ?? ""}
              onChange={(v) => updateIntent("good_answer_looks_like", v)}
              rows={3}
            />
          </div>

          {/* Answer Quality Notes */}
          {result?.evaluation.answer_quality && (
            <div className="mt-4 rounded-md bg-blue-50 p-3">
              <p className="text-xs font-medium text-blue-900">Quality Notes</p>
              <div className="mt-2 space-y-1 text-xs text-blue-800">
                {result.evaluation.answer_quality.clarity_note && (
                  <p><strong>Clarity:</strong> {result.evaluation.answer_quality.clarity_note}</p>
                )}
                {result.evaluation.answer_quality.completeness_note && (
                  <p><strong>Completeness:</strong> {result.evaluation.answer_quality.completeness_note}</p>
                )}
                {result.evaluation.answer_quality.actionability_note && (
                  <p><strong>Actionability:</strong> {result.evaluation.answer_quality.actionability_note}</p>
                )}
              </div>
            </div>
          )}

          {/* Regenerated Answer */}
          {result?.regeneration && (
            <div className="mt-4 border-t border-slate-200 pt-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-medium text-slate-700">Improved Answer</p>
                <button
                  onClick={() =>
                    navigator.clipboard.writeText(result.regeneration!.improved_answer)
                  }
                  className="rounded px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
                >
                  Copy
                </button>
              </div>
              <div className="prose prose-sm max-h-96 overflow-y-auto rounded-md border border-slate-200 bg-slate-50 p-3">
                <div className="whitespace-pre-wrap text-slate-800">
                  {result.regeneration.improved_answer}
                </div>
              </div>

              {/* Changes Summary */}
              {result.regeneration.changes_summary.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-medium text-slate-700">Changes Summary</p>
                  <ul className="mt-2 space-y-1">
                    {result.regeneration.changes_summary.map((change, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-slate-700">
                        <span className="mt-0.5 text-green-600">✓</span>
                        <span>{change}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </AccordionItem>
      </div>
      )}
    </aside>
  );
}

/* Subcomponents */

function AccordionItem({
  title,
  children,
  isExpanded,
  onToggle,
}: {
  title: string;
  children: React.ReactNode;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <section className="rounded-lg border border-slate-200">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-4 py-3 text-left transition hover:bg-slate-50"
      >
        <h3 className="font-medium text-slate-900">{title}</h3>
        <span className="text-slate-400">{isExpanded ? "▼" : "▶"}</span>
      </button>
      {isExpanded && <div className="border-t border-slate-200 p-4">{children}</div>}
    </section>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    verified: "bg-green-100 text-green-700",
    needs_verification: "bg-yellow-100 text-yellow-700",
    unsupported: "bg-red-100 text-red-700",
    not_applicable: "bg-slate-100 text-slate-600",
  };

  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] || "bg-slate-100"}`}>
      {status.replace(/_/g, " ")}
    </span>
  );
}

function IntentField({
  label,
  value,
  onChange,
  placeholder,
  rows = 2,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  rows?: number;
}) {
  return (
    <label className="block text-xs text-slate-600">
      {label}
      <textarea
        className="mt-1 w-full rounded border border-slate-200 px-2 py-1.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none"
        rows={rows}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
