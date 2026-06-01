import type { AttributionResult } from "../../types/evaluation";

interface AttributionChainsProps {
  attribution: AttributionResult | null;
}

export function AttributionChains({ attribution }: AttributionChainsProps) {
  if (!attribution?.chains.length) {
    return (
      <p className="mt-2 text-xs text-slate-500">
        Attribution chains appear after evaluate (Claim → Reasoning → Source → Evidence).
      </p>
    );
  }

  // Extract unique sources used
  const sourcesUsed = new Map<string, { label: string; source_type?: string }>();
  for (const chain of attribution.chains) {
    if (chain.source) {
      const key = chain.source.label;
      if (!sourcesUsed.has(key)) {
        sourcesUsed.set(key, {
          label: chain.source.label,
          source_type: chain.source.source_type as string | undefined,
        });
      }
    }
  }

  if (sourcesUsed.size === 0) {
    return null;
  }

  return (
    <div className="mt-3">
      <p className="mb-2 text-xs font-medium text-slate-700">Sources used:</p>
      <ul className="space-y-1">
        {Array.from(sourcesUsed.values()).map((source, i) => (
          <li key={i} className="rounded border border-slate-200 bg-white px-3 py-2 text-sm">
            <p className="font-medium text-slate-800">{source.label}</p>
            {source.source_type && (
              <p className="mt-0.5 text-xs text-slate-500 capitalize">{source.source_type.replace(/_/g, " ")}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
