import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  AnswerQualityIntent,
  Citation,
  CustomSource,
  EvaluationRequest,
  EvaluationResponse,
  SourcePreferences,
} from "../types/evaluation";
import {
  ALL_CRITERIA,
  DEFAULT_SOURCE_PREFERENCES,
  buildDefaultEvaluateRequest,
} from "../types/evaluation";
import { evaluate, uploadFile } from "../api/client";

const DRAFT_KEY = "evaluation-form-draft";

export type FormStatus = "idle" | "submitting" | "done" | "error";

export interface EvaluationFormState {
  aiResponse: string;
  userQuery: string;
  claimVerificationEnabled: boolean;
  sourcePreferences: SourcePreferences;
  answerQualityIntent: AnswerQualityIntent;
  customSources: CustomSource[];
  citations: Citation[];
  pastedContext: string;
  contextUrls: string[];
  fileIds: string[];
  pendingFiles: File[];
  regenerate: boolean;
  status: FormStatus;
  result: EvaluationResponse | null;
  error: string | null;
}

const defaultIntent: AnswerQualityIntent = {
  user_intent: "",
  expertise_level: "intermediate",
  user_goal: "",
  constraints_or_expectations: "",
  good_answer_looks_like: "",
};

function loadDraft(): Partial<EvaluationFormState> | null {
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    return raw ? (JSON.parse(raw) as Partial<EvaluationFormState>) : null;
  } catch {
    return null;
  }
}

export function useEvaluationForm(initialResponse = "") {
  const draft = useMemo(() => loadDraft(), []);

  const [aiResponse, setAiResponse] = useState(
    draft?.aiResponse ?? initialResponse,
  );
  const [userQuery, setUserQuery] = useState(draft?.userQuery ?? "");
  const [claimVerificationEnabled, setClaimVerificationEnabled] = useState(
    draft?.claimVerificationEnabled ?? false,
  );
  const [sourcePreferences, setSourcePreferences] = useState<SourcePreferences>(
    draft?.sourcePreferences ?? DEFAULT_SOURCE_PREFERENCES,
  );
  const [answerQualityIntent, setAnswerQualityIntent] =
    useState<AnswerQualityIntent>(draft?.answerQualityIntent ?? defaultIntent);
  const [customSources, setCustomSources] = useState<CustomSource[]>(
    draft?.customSources ?? [],
  );
  const [citations, setCitations] = useState<Citation[]>(draft?.citations ?? []);
  const [pastedContext, setPastedContext] = useState(draft?.pastedContext ?? "");
  const [contextUrls, setContextUrls] = useState<string[]>(
    draft?.contextUrls ?? [],
  );
  const [fileIds, setFileIds] = useState<string[]>(draft?.fileIds ?? []);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [regenerate, setRegenerate] = useState(draft?.regenerate ?? true);
  const [status, setStatus] = useState<FormStatus>("idle");
  const [result, setResult] = useState<EvaluationResponse | null>(null);
  const [error, setErrorState] = useState<string | null>(null);
  const setError = setErrorState;

  const canEvaluate = aiResponse.trim().length > 0;

  useEffect(() => {
    const draftPayload = {
      aiResponse,
      userQuery,
      claimVerificationEnabled,
      sourcePreferences,
      answerQualityIntent,
      customSources,
      citations,
      pastedContext,
      contextUrls,
      fileIds,
      regenerate,
    };
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draftPayload));
  }, [
    aiResponse,
    userQuery,
    claimVerificationEnabled,
    sourcePreferences,
    answerQualityIntent,
    customSources,
    citations,
    pastedContext,
    contextUrls,
    fileIds,
    regenerate,
  ]);

  const buildRequest = useCallback((): EvaluationRequest => {
    return buildDefaultEvaluateRequest(aiResponse, {
      user_query: userQuery || null,
      claim_verification_enabled: claimVerificationEnabled,
      source_preferences: sourcePreferences,
      custom_sources: customSources,
      citations,
      regenerate,
      answer_quality_intent: answerQualityIntent,
      user_context: {
        file_ids: fileIds,
        pasted_text: pastedContext,
        urls: contextUrls.filter((u) => u.trim()),
      },
    });
  }, [
    aiResponse,
    userQuery,
    claimVerificationEnabled,
    sourcePreferences,
    customSources,
    citations,
    regenerate,
    answerQualityIntent,
    fileIds,
    pastedContext,
    contextUrls,
  ]);

  const addFiles = useCallback(async (files: FileList | File[]) => {
    const list = Array.from(files);
    setPendingFiles((prev) => [...prev, ...list]);
    const ids: string[] = [];
    for (const file of list) {
      const { file_id } = await uploadFile(file);
      ids.push(file_id);
    }
    setFileIds((prev) => [...prev, ...ids]);
  }, []);

  const submitEvaluate = useCallback(async () => {
    if (!canEvaluate) return;
    setStatus("submitting");
    setError(null);
    try {
      const response = await evaluate(buildRequest());
      setResult(response);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Evaluation failed");
      setStatus("error");
    }
  }, [buildRequest, canEvaluate]);

  return {
    aiResponse,
    setAiResponse,
    userQuery,
    setUserQuery,
    claimVerificationEnabled,
    setClaimVerificationEnabled,
    sourcePreferences,
    setSourcePreferences,
    answerQualityIntent,
    setAnswerQualityIntent,
    customSources,
    setCustomSources,
    citations,
    setCitations,
    pastedContext,
    setPastedContext,
    contextUrls,
    setContextUrls,
    fileIds,
    pendingFiles,
    addFiles,
    regenerate,
    setRegenerate,
    status,
    result,
    error,
    setError,
    canEvaluate,
    submitEvaluate,
    criteria: [...ALL_CRITERIA],
  };
}
