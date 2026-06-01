import type { CustomSource } from "../../types/evaluation";

interface ContextInputsProps {
  pastedContext: string;
  onPastedContextChange: (v: string) => void;
  contextUrls: string[];
  onContextUrlsChange: (urls: string[]) => void;
  customSources: CustomSource[];
  onCustomSourcesChange: (sources: CustomSource[]) => void;
  onFilesSelected: (files: FileList) => void;
  uploadedCount: number;
  pendingFileNames: string[];
}

export function ContextInputs({
  pastedContext,
  onPastedContextChange,
  contextUrls,
  onContextUrlsChange,
  customSources,
  onCustomSourcesChange,
  onFilesSelected,
  uploadedCount,
  pendingFileNames,
}: ContextInputsProps) {
  const addCustomSource = () => {
    onCustomSourcesChange([
      ...customSources,
      { label: "", url: null, notes: "" },
    ]);
  };

  const updateUrl = (index: number, value: string) => {
    const next = [...contextUrls];
    next[index] = value;
    onContextUrlsChange(next);
  };

  return (
    <div className="mt-6 space-y-4 rounded-lg border border-slate-200 bg-white p-5">
      <h2 className="text-base font-semibold text-slate-800">Sources</h2>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-slate-700">
          Upload files (.txt, .md, .pdf)
        </label>
        <input
          type="file"
          multiple
          accept=".txt,.md,.pdf"
          className="mt-2 block w-full text-sm file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200"
          onChange={(e) => e.target.files && onFilesSelected(e.target.files)}
        />
        {uploadedCount > 0 && (
          <p className="mt-2 text-sm text-green-700">✓ {uploadedCount} file(s) uploaded</p>
        )}
        {pendingFileNames.length > 0 && (
          <p className="mt-1 text-xs text-slate-500">Uploading: {pendingFileNames.join(", ")}</p>
        )}
      </div>

      {/* URL Sources */}
      <div>
        <p className="text-sm font-medium text-slate-700">Link URLs</p>
        <div className="mt-2 space-y-2">
          {contextUrls.map((url, i) => (
            <input
              key={i}
              className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              placeholder="https://example.com/article"
              value={url}
              onChange={(e) => updateUrl(i, e.target.value)}
            />
          ))}
        </div>
        <button
          type="button"
          className="mt-2 text-sm text-blue-600 hover:underline"
          onClick={() => onContextUrlsChange([...contextUrls, ""])}
        >
          + Add URL
        </button>
      </div>

      {/* Pasted Context */}
      <label className="block">
        <span className="text-sm font-medium text-slate-700">Paste supporting context</span>
        <textarea
          className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          rows={4}
          value={pastedContext}
          onChange={(e) => onPastedContextChange(e.target.value)}
          placeholder="Paste any supporting text, data, or notes here..."
        />
      </label>

      {/* Custom Sources */}
      <div>
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-slate-700">Custom sources</p>
          <button
            type="button"
            className="text-sm text-blue-600 hover:underline"
            onClick={addCustomSource}
          >
            + Add your own source
          </button>
        </div>
        {customSources.map((src, i) => (
          <div key={i} className="mt-3 space-y-2 rounded-md border border-slate-200 p-3">
            <input
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              placeholder="Source label"
              value={src.label}
              onChange={(e) => {
                const next = [...customSources];
                next[i] = { ...src, label: e.target.value };
                onCustomSourcesChange(next);
              }}
            />
            <input
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              placeholder="URL (optional)"
              value={src.url ?? ""}
              onChange={(e) => {
                const next = [...customSources];
                next[i] = { ...src, url: e.target.value || null };
                onCustomSourcesChange(next);
              }}
            />
            <textarea
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              placeholder="Notes or excerpts"
              rows={2}
              value={src.notes ?? ""}
              onChange={(e) => {
                const next = [...customSources];
                next[i] = { ...src, notes: e.target.value };
                onCustomSourcesChange(next);
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
