function getApiBase(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL || "/api";
  if (typeof window !== "undefined") {
    const runningOnLocalhost = window.location.hostname === "localhost";
    const targetsLocalhost =
      configured.includes("localhost") || configured.includes("127.0.0.1");
    // Guard against stale production env accidentally pointing to localhost.
    if (!runningOnLocalhost && targetsLocalhost) {
      return "/api";
    }
  }
  return configured;
}

type RequestOptions = {
  token?: string;
  method?: string;
  body?: unknown;
};

async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  const apiBase = getApiBase();
  let res: Response;
  try {
    res = await fetch(`${apiBase}${path}`, {
      cache: "no-store",
      method: options.method || "GET",
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error(
      "Network error: cannot reach API. Verify NEXT_PUBLIC_API_BASE_URL and proxy routing."
    );
  }
  if (!res.ok) {
    let detail = "";
    try {
      const body = (await res.json()) as { detail?: string };
      detail = body?.detail ? `: ${body.detail}` : "";
    } catch {
      detail = "";
    }
    throw new Error(`API error ${res.status}${detail}`);
  }
  return res.json() as Promise<T>;
}

export type DashboardMetrics = {
  total_applications: number;
  applied_count: number;
  interview_count: number;
  response_rate: number;
  pending_follow_ups: number;
};

export type JobPosting = {
  id: number;
  title: string;
  company: string;
  location?: string | null;
  source: string;
  url?: string | null;
  created_at: string;
};

export type Application = {
  id: number;
  job_posting_id: number;
  status: string;
  notes?: string | null;
  next_follow_up_at?: string | null;
  updated_at: string;
};

export type Document = {
  id: number;
  application_id: number;
  kind: string;
  title: string;
  content?: string;
  version: number;
  created_at: string;
};

export type JobImportPayload = {
  source?: string;
  external_id?: string;
  title: string;
  company: string;
  location?: string;
  description?: string;
  url?: string;
};

export type ApplicationCreatePayload = {
  job_posting_id: number;
  status?: string;
  notes?: string;
};

export type CoverLetterPayload = {
  application_id: number;
  profile_context: string;
  company: string;
  role: string;
  job_description: string;
};

export type FitScorePayload = {
  application_id: number;
  profile_context: string;
  job_description?: string;
};

export type ReviewPayload = {
  application_id: number;
  resume_text: string;
  cover_letter: string;
  job_description: string;
};

export type AIResponse = {
  result: string;
};

export type LinkedInSessionBootstrapPayload = {
  session_id?: string;
  cookies_json?: string;
  cookie_header?: string;
  user_agent?: string;
};

export type LinkedInApplyPayload = {
  job_url: string;
  session_id?: string;
  draft?: {
    full_name?: string;
    email?: string;
    phone?: string;
    cover_letter?: string;
  };
};

export type LinkedInTaskResponse = {
  task_id: string;
  status: string;
  ready: boolean;
  successful: boolean;
  result?: unknown;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export const api = {
  login: (username: string, password: string) =>
    apiRequest<LoginResponse>("/auth/login", {
      method: "POST",
      body: { username, password },
    }),
  metrics: (token: string) =>
    apiRequest<DashboardMetrics>("/applications/dashboard/metrics", { token }),
  jobs: (token: string) => apiRequest<JobPosting[]>("/jobs", { token }),
  importJob: (token: string, payload: JobImportPayload) =>
    apiRequest<JobPosting>("/jobs/import", { token, method: "POST", body: payload }),
  applications: (token: string) => apiRequest<Application[]>("/applications", { token }),
  createApplication: (token: string, payload: ApplicationCreatePayload) =>
    apiRequest<Application>("/applications", { token, method: "POST", body: payload }),
  documents: (token: string) => apiRequest<Document[]>("/documents", { token }),
  generateCoverLetter: (token: string, payload: CoverLetterPayload) =>
    apiRequest<Document>("/ai/cover-letter", { token, method: "POST", body: payload }),
  fitScore: (token: string, payload: FitScorePayload) =>
    apiRequest<AIResponse>("/ai/fit-score", { token, method: "POST", body: payload }),
  reviewApplication: (token: string, payload: ReviewPayload) =>
    apiRequest<AIResponse>("/ai/review", { token, method: "POST", body: payload }),
  linkedinBootstrapSession: (token: string, payload: LinkedInSessionBootstrapPayload) =>
    apiRequest<{ ok: boolean; session_id: string; cookie_count: number }>(
      "/linkedin/automation/session/bootstrap",
      { token, method: "POST", body: payload }
    ),
  linkedinApplyDraft: (token: string, payload: LinkedInApplyPayload) =>
    apiRequest<{ ok: boolean; task_id: string; status: string }>(
      "/linkedin/automation/apply",
      { token, method: "POST", body: payload }
    ),
  linkedinTaskStatus: (token: string, taskId: string) =>
    apiRequest<LinkedInTaskResponse>(`/linkedin/automation/tasks/${taskId}`, { token }),
};
