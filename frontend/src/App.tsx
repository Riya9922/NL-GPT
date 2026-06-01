import { EvaluationPanel } from "./components/panel/EvaluationPanel";
import { HighlightedResponse } from "./components/highlights/HighlightedResponse";
import { useEvaluationForm } from "./hooks/useEvaluationForm";

const SAMPLE_RESPONSE =
  "Users prefer convenience. Price sensitivity is secondary to ease of access.";

export default function App() {
  const form = useEvaluationForm(SAMPLE_RESPONSE);
  const showHighlights =
    form.claimVerificationEnabled && form.status === "done" && !!form.result;

  const handleEvaluate = async () => {
    await form.submitEvaluate();
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Left Column: Response */}
      <main className="flex flex-1 flex-col overflow-y-auto p-6">
        <div className="mb-4">
          <h1 className="text-2xl font-semibold text-slate-900">
            AI Output Evaluation
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Evaluate AI responses with claims, sources, reasoning, and regeneration
          </p>
        </div>

        <label className="mb-4 block text-sm font-medium text-slate-700">
          Your question
          <input
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={form.userQuery}
            onChange={(e) => form.setUserQuery(e.target.value)}
            placeholder="What did you ask the AI?"
          />
        </label>

        <label className="mb-4 block text-sm font-medium text-slate-700">
          AI response
        </label>
        {showHighlights ? (
          <HighlightedResponse
            text={form.aiResponse}
            analysis={form.result!.analysis}
            evaluation={form.result!.evaluation}
            enabled
          />
        ) : (
          <textarea
            className="mt-1 min-h-[280px] w-full rounded-lg border border-slate-200 px-3 py-2 text-sm font-mono focus:border-blue-500 focus:outline-none"
            value={form.aiResponse}
            onChange={(e) => form.setAiResponse(e.target.value)}
            placeholder="Paste the AI response here..."
          />
        )}
      </main>

      {/* Right Column: Evaluation Panel */}
      <EvaluationPanel
        claimVerificationEnabled={form.claimVerificationEnabled}
        onClaimVerificationEnabledChange={form.setClaimVerificationEnabled}
        sourcePreferences={form.sourcePreferences}
        onSourcePreferencesChange={form.setSourcePreferences}
        answerQualityIntent={form.answerQualityIntent}
        onAnswerQualityIntentChange={form.setAnswerQualityIntent}
        regenerate={form.regenerate}
        onRegenerateChange={form.setRegenerate}
        onEvaluate={handleEvaluate}
        loading={form.status === "submitting"}
        canEvaluate={form.canEvaluate}
        result={form.result}
        error={form.error}
      />
    </div>
  );
}
