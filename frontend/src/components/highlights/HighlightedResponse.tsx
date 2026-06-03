import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import type {
  AnalysisResult,
  ClaimVerificationStatus,
  EvaluationResult,
} from "../../types/evaluation";

interface HighlightedResponseProps {
  text: string;
  analysis: AnalysisResult | null;
  evaluation: EvaluationResult | null;
  enabled: boolean;
}

interface Segment {
  start: number;
  end: number;
  status: ClaimVerificationStatus;
  claimId: string;
  note?: string | null;
}

const STATUS_CLASS: Record<ClaimVerificationStatus, string> = {
  verified: "bg-highlight-verified hover:bg-green-100",
  needs_verification: "bg-highlight-pending hover:bg-yellow-100",
  unsupported: "bg-highlight-pending hover:bg-yellow-100",
  not_applicable: "bg-highlight-pending hover:bg-yellow-100",
};

const STATUS_BADGE_CLASS: Record<ClaimVerificationStatus, string> = {
  verified: "bg-green-600 text-white",
  needs_verification: "bg-yellow-600 text-white",
  unsupported: "bg-yellow-600 text-white",
  not_applicable: "bg-yellow-600 text-white",
};

export function HighlightedResponse({
  text,
  analysis,
  evaluation,
  enabled,
}: HighlightedResponseProps) {
  const [activeId, setActiveId] = useState<string | null>(null);

  const segments = useMemo(() => {
    if (!enabled || !analysis || !evaluation?.claims.length) return [];

    const statusByClaim = new Map(
      evaluation.claims.map((c) => [c.claim_id, c]),
    );

    const segs: Segment[] = [];
    for (const claim of analysis.claims) {
      const evaluated = statusByClaim.get(claim.id);
      if (!evaluated || !claim.span) continue;
      segs.push({
        start: claim.span.start,
        end: claim.span.end,
        status: evaluated.status,
        claimId: claim.id,
        note: evaluated.verification_note,
      });
    }

    return segs.sort((a, b) => a.start - b.start);
  }, [analysis, evaluation, enabled]);

  const activeEvaluated = evaluation?.claims.find((c) => c.claim_id === activeId);

  if (!enabled || segments.length === 0) {
    return (
      <div className="mt-1 min-h-[280px] whitespace-pre-wrap rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 prose prose-sm max-w-none">
        <ReactMarkdown rehypePlugins={[rehypeRaw]}>{text}</ReactMarkdown>
      </div>
    );
  }

  let markdownString = "";
  let cursor = 0;

  segments.forEach((seg) => {
    if (seg.start > cursor) {
      markdownString += text.slice(cursor, seg.start);
    }
    // We inject HTML marks with data attributes for hover events
    markdownString += `<mark data-claim-id="${seg.claimId}" class="cursor-pointer rounded px-0.5 ${STATUS_CLASS[seg.status]}">`;
    markdownString += text.slice(seg.start, seg.end);
    markdownString += `</mark>`;
    cursor = Math.max(cursor, seg.end);
  });

  if (cursor < text.length) {
    markdownString += text.slice(cursor);
  }

  return (
    <div className="relative">
      <div className="mt-1 min-h-[280px] rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm leading-relaxed text-slate-800 prose prose-sm max-w-none">
        <ReactMarkdown
          rehypePlugins={[rehypeRaw]}
          components={{
            mark: ({ node, ...props }) => {
              const claimId = (props as any)["data-claim-id"] as string;
              return (
                <mark
                  {...props}
                  onMouseEnter={() => setActiveId(claimId)}
                  onMouseLeave={() => setActiveId(null)}
                  tabIndex={0}
                  role="mark"
                />
              );
            },
          }}
        >
          {markdownString}
        </ReactMarkdown>
      </div>
      {activeId && activeEvaluated && (
        <div 
          className="absolute left-3 top-3 z-20 w-80 rounded-lg border border-slate-200 bg-white p-4 shadow-xl"
          onMouseEnter={() => setActiveId(activeId)}
          onMouseLeave={() => setActiveId(null)}
        >
          <div className="mb-2 flex items-center gap-2">
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                STATUS_BADGE_CLASS[activeEvaluated.status]
              }`}
            >
              {activeEvaluated.status.replace(/_/g, " ")}
            </span>
            <span className="font-mono text-xs text-slate-500">{activeEvaluated.claim_id}</span>
          </div>
          
          {activeEvaluated.sources.length > 0 && (
            <div className="mb-2">
              <p className="mb-1 text-xs font-medium text-slate-700">Sources:</p>
              <ul className="space-y-1">
                {activeEvaluated.sources.slice(0, 3).map((s, idx) => (
                  <li key={idx} className="text-xs">
                    {s.url ? (
                      <a
                        href={s.url}
                        className="text-blue-600 underline hover:text-blue-800"
                        target="_blank"
                        rel="noreferrer"
                      >
                        {s.title}
                      </a>
                    ) : (
                      <span className="text-slate-700">{s.title}</span>
                    )}
                    {s.snippet && (
                      <p className="mt-0.5 text-slate-500 line-clamp-2">{s.snippet}</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {activeEvaluated.verification_note && (
            <div className="rounded-md bg-slate-50 p-2">
              <p className="text-xs text-slate-700">{activeEvaluated.verification_note}</p>
            </div>
          )}
        </div>
      )}
      <p className="mt-2 text-xs text-slate-500">
        Green = verified · Yellow = needs verification. Turn on
        claim verification and re-evaluate to refresh highlights.
      </p>
    </div>
  );
}
