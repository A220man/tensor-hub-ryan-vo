export type IssueCategory =
  | 'segfault'
  | 'performance'
  | 'memory'
  | 'logic_bug'
  | 'platform_specific'
  | 'feature_request'
  | 'unknown';

export type IssueStatus =
  | 'new'
  | 'analyzing'
  | 'analyzed'
  | 'test_generated'
  | 'closed';

export type TestCaseStatus =
  | 'generated'
  | 'verified'
  | 'failed';

export interface IssueBase {
  github_number?: number;
  title: string;
  body: string;
  html_url?: string;
  php_version?: string;
  os?: string;
  comments_count: number;
}

export interface IssueCreate extends IssueBase {}

export interface IssueUpdate {
  title?: string;
  body?: string;
  html_url?: string;
  php_version?: string;
  os?: string;
  category?: IssueCategory;
  status?: IssueStatus;
}

export interface IssueResponse extends IssueBase {
  id: number;
  category: IssueCategory;
  status: IssueStatus;
  created_at: string;
  updated_at: string;
}

export interface IssueListResponse {
  items: IssueResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface AnalysisBase {
  classification: string;
  stack_trace?: string;
  error_patterns?: string[];
  root_cause?: string;
  suggested_fix?: string;
  confidence: number;
}

export interface AnalysisCreate extends AnalysisBase {}

export interface AnalysisResponse extends AnalysisBase {
  id: number;
  issue_id: number;
  created_at: string;
}

export interface TestCaseBase {
  language: string;
  code: string;
  description?: string;
  expected_behavior?: string;
}

export interface TestCaseCreate extends TestCaseBase {}

export interface TestCaseResponse extends TestCaseBase {
  id: number;
  issue_id: number;
  status: TestCaseStatus;
  created_at: string;
}

export interface AnalyzeRequest {
  title: string;
  body: string;
  php_version?: string;
  os?: string;
}

export interface AnalyzeResponse {
  issue: IssueResponse;
  analysis: AnalysisResponse;
  test_case?: TestCaseResponse;
}