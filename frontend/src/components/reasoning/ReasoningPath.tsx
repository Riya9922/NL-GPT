import { useState } from "react";
import type { LogicEvaluation } from "../../types/evaluation";

interface ReasoningPathProps {
  logic: LogicEvaluation;
}

export function ReasoningPath({ logic }: ReasoningPathProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const toggle = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="mt-2 space-y-4 text-sm">
      {/* Conclusion */}
      <div>
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Conclusion
        </p>
        <p className="text-slate-800">{logic.conclusion}</p>
      </div>

      {/* Reasoning Path */}
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Reasoning Path
        </p>
        <ol className="space-y-2">
          {logic.reasoning_path.map((step) => (
            <li key={step.step_id} className="rounded border border-slate-200 bg-white p-2">
              <button
                type="button"
                className="flex w-full items-start gap-2 text-left"
                onClick={() => toggle(step.step_id)}
                aria-expanded={!!expanded[step.step_id]}
              >
                <span className="text-slate-400">{expanded[step.step_id] ? "▾" : "▸"}</span>
                <span className="text-slate-700">{step.text}</span>
              </button>
              {expanded[step.step_id] && (
                <div className="mt-2 border-l-2 border-slate-200 pl-4 text-xs text-slate-600">
                  {step.expandable_detail ? (
                    <p className="whitespace-pre-wrap">{step.expandable_detail}</p>
                  ) : null}
                  {step.evidence_links.length > 0 && (
                    <ul className="mt-1 list-disc pl-4">
                      {step.evidence_links.map((link, i) => (
                        <li key={i}>
                          {link.url ? (
                            <a
                              href={link.url}
                              className="text-blue-600 underline hover:text-blue-800"
                              target="_blank"
                              rel="noreferrer"
                            >
                              {link.label}
                            </a>
                          ) : (
                            link.label
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                  {!step.expandable_detail && step.evidence_links.length === 0 && (
                    <p>No additional evidence in this mock step.</p>
                  )}
                </div>
              )}
            </li>
          ))}
        </ol>a
      </div>

      {/* Assumptions */}
      {logic.logical_gaps.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Assumptions
          </p>
          <ul className="space-y-1.5">
            {logic.logical_gaps.map((gap, i) => (
              <li key={i} className="rounded border border-slate-200 bg-white p-2 text-sm text-slate-700">
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Alternative Perspectives */}
      {logic.alternate_perspectives.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Alternative Perspectives
          </p>
          <ul className="space-y-2">
            {logic.alternate_perspectives.map((p, i) => (
              <li key={i} className="rounded border border-slate-200 bg-white p-2 text-sm text-slate-700">
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
