/** Mirrors backend Pydantic contracts — Phase 1 */

export const ALL_CRITERIA = [
  "claim_verification",
  "source_transparency",
  "logic_reasoning",
  "missing_factors",
  "improve_answer_quality",
] as const;

export type Criteria = (typeof ALL_CRITERIA)[number];

export type ClaimType = "factual" | "opinion" | "prediction";

export type ClaimVerificationStatus =
  | "verified"
  | "needs_verification"
  | "unsupported"
  | "not_applicable";

export type SourceType =
  | "memory"
  | "user_context"
  | "web"
  | "research"
  | "company"
  | "internal"
  | "custom";

export type EvaluationStatus = "processing" | "completed" | "failed";

export interface SourcePreferences {
  memory: boolean;
  user_context: boolean;
  web: boolean;
  research: boolean;
  company: boolean;
  internal: boolean;
}

export interface AnswerQualityIntent {
  user_intent?: string | null;
  expertise_level?: string | null;
  user_goal?: string | null;
  constraints_or_expectations?: string | null;
  good_answer_looks_like?: string | null;
}

export interface EvaluationRequest {
  user_query?: string | null;
  ai_response: string;
  conversation_id?: string | null;
  criteria: Criteria[];
  claim_verification_enabled: boolean;
  source_preferences: SourcePreferences;
  custom_sources?: CustomSource[];
  user_context?: UserContext | null;
  citations?: Citation[];
  regenerate?: boolean;
  answer_quality_intent?: AnswerQualityIntent | null;
}

export interface CustomSource {
  label: string;
  url?: string | null;
  notes?: string | null;
}

export interface UserContext {
  file_ids?: string[];
  pasted_text?: string;
  urls?: string[];
}

export interface Citation {
  index: number;
  title?: string | null;
  url?: string | null;
  raw?: string | null;
}

export interface TextSpan {
  start: number;
  end: number;
}

export interface Claim {
  id: string;
  text: string;
  span: TextSpan | null;
  type: ClaimType;
}

export interface Assumption {
  id: string;
  text: string;
  related_claim_ids: string[];
  derived_from_hint?: string | null;
}

export interface ReasoningStep {
  id: string;
  step: string;
  order: number;
  supports_claim_ids: string[];
}

export interface AnalysisResult {
  claims: Claim[];
  assumptions: Assumption[];
  reasoning_steps: ReasoningStep[];
  unsupported_statements: string[];
  completeness_notes: string;
}

export interface ClaimAttributionChain {
  claim_id: string;
  claim_text: string;
  reasoning_step: { step_id?: string | null; text?: string | null } | null;
  source: {
    source_id?: string | null;
    source_type?: SourceType | null;
    label: string;
    url?: string | null;
    citation_index?: number | null;
  } | null;
  evidence: {
    supporting: { text: string; excerpt?: string | null }[];
    counter: { text: string; excerpt?: string | null }[];
  };
  assumption: {
    text: string;
    derived_from?: string | null;
    supporting_evidence?: string | null;
    counter_evidence?: string | null;
  } | null;
  attribution_gap: string | null;
}

export interface AttributionResult {
  chains: ClaimAttributionChain[];
  unlinked_claims: string[];
  meta: {
    sources_respected: string[];
    chains_complete: number;
    chains_with_gaps: number;
  };
}

export interface MissingFactor {
  heading: string;
  summary: string;
}

export interface EvaluationResult {
  claims: EvaluatedClaim[];
  source_analysis: SourceAnalysis;
  logic: LogicEvaluation;
  missing_factors: MissingFactor[];
  answer_quality: AnswerQualityNotes | null;
}

export interface EvaluatedClaim {
  claim_id: string;
  status: ClaimVerificationStatus;
  sources: VerificationSource[];
  verification_note?: string | null;
}

export interface VerificationSource {
  title: string;
  url?: string | null;
  source_type: SourceType;
  snippet?: string | null;
}

export interface SourceUsedItem {
  source_type: SourceType;
  label: string;
  url?: string | null;
}

export interface SourceAnalysis {
  sources_used: SourceUsedItem[];
  trust_issues: string[];
  missing_source_types: string[];
}

export interface LogicEvaluation {
  conclusion: string;
  reasoning_path: ReasoningPathStep[];
  logical_gaps: string[];
  alternate_perspectives: string[];
  critique: string;
}

export interface ReasoningPathStep {
  step_id: string;
  text: string;
  evidence_links: { url?: string | null; label: string }[];
  expandable_detail?: string | null;
}

export interface AnswerQualityNotes {
  clarity_note?: string | null;
  completeness_note?: string | null;
  actionability_note?: string | null;
  summary?: string | null;
}

export interface RegenerationResult {
  improved_answer: string;
  changes_summary: string[];
  recommended_inputs: string[];
  addressed_criteria: Criteria[];
}

export interface EvaluationMeta {
  model: string;
  duration_ms: number;
  claim_verification_enabled: boolean;
  dimensions: Criteria[];
}

export interface EvaluationResponse {
  evaluation_id: string;
  status: EvaluationStatus;
  analysis: AnalysisResult;
  attribution: AttributionResult;
  evaluation: EvaluationResult;
  regeneration: RegenerationResult | null;
  meta: EvaluationMeta;
}

export const DIMENSION_LABELS: Record<Criteria, string> = {
  claim_verification: "Claim Verification",
  source_transparency: "Source Transparency",
  logic_reasoning: "Logic & Reasoning Check",
  missing_factors: "Missing Factors",
  improve_answer_quality: "Improve Answer Quality",
};

export const DEFAULT_SOURCE_PREFERENCES: SourcePreferences = {
  memory: true,
  user_context: true,
  web: true,
  research: true,
  company: true,
  internal: true,
};

export function buildDefaultEvaluateRequest(
  aiResponse: string,
  overrides?: Partial<EvaluationRequest>,
): EvaluationRequest {
  return {
    ai_response: aiResponse,
    criteria: [...ALL_CRITERIA],
    claim_verification_enabled: false,
    source_preferences: DEFAULT_SOURCE_PREFERENCES,
    regenerate: true,
    ...overrides,
  };
}
