export type RunStatus = 'queued' | 'running' | 'done' | 'failed';

export interface Policy {
  policy_id: string;
  name: string;
  language: string;
  version: string;
  spec: unknown;
  created_at: string;
}

export interface RunSummary {
  run_id: string;
  user_id?: string;
  status: RunStatus;
  language: string;
  model_version: string;
  compliance_score: number | null;
  started_at: string;
  finished_at: string | null;
}

export interface Finding {
  finding_id: string;
  run_id: string;
  rule_id: string;
  file_path: string;
  line: number;
  severity: 'low' | 'medium' | 'high';
  status: 'open' | 'fixed' | 'ignored';
  evidence: Record<string, unknown>;
}

export interface Metric {
  metric_id: string;
  run_id: string;
  name: string;
  before: number | null;
  after: number | null;
}

export interface Artifact {
  artifact_id: string;
  run_id: string;
  type: 'report_html' | 'report_json' | 'patch' | 'log';
  uri: string;
  checksum: string;
  created_at: string;
}

export interface RunDetail extends RunSummary {
  findings: Finding[];
  metrics: Metric[];
  artifacts: Artifact[];
}

export interface StartRefactorPayload {
  language: 'python' | 'terraform';
  mode: 'auto' | 'suggest';
  run_tests: boolean;
  files: { path: string; content: string }[];
  policy_ids: string[];
}

export interface StartRefactorResponse {
  run_id: string;
}

export interface PolicyProfile {
  name: string;
  domain: string;
  version: string;
  policy_profile_id: string;
  rules: unknown;
}

export interface RefactorRequestPayload {
  user_id: string;
  user_name: string;
  code: string;
  language: 'python' | 'terraform';
  policy_profile_id: string;
  repo?: string | null;
  branch?: string | null;
  file_path?: string | null;
}

export interface Suggestion {
  suggestion_id: string;
  file_path: string;
  start_line: number;
  end_line: number;
  original_code: string;
  proposed_code: string;
  rationale: string;
  confidence_score: number;
}

export interface ComplianceSummary {
  policy_score: number;
  complexity_delta: number;
  test_pass_rate: number;
  latency_ms: number;
  token_usage: number;
}

export interface Violation {
  rule_key: string;
  message: string;
  severity: 'low' | 'medium' | 'high';
}

export interface RefactorResult {
  session: {
    session_id: string;
    status: string;
    language: string;
    policy_profile_id: string;
  };
  suggestions: Suggestion[];
  compliance: ComplianceSummary;
  original_code: string;
  refactored_code: string;
  violations: Violation[];
}

export interface ImportPolicyPayload {
  name?: string | null;
  domain?: string | null;
  version?: string | null;
  document: string;
}

export interface ImportPolicyResponse {
  name: string;
  policy_profile_id: string;
}