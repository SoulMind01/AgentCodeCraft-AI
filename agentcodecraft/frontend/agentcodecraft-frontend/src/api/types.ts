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