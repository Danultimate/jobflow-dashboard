const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost/api";

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
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    method: options.method || "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
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
  version: number;
  created_at: string;
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
  applications: (token: string) => apiRequest<Application[]>("/applications", { token }),
  documents: (token: string) => apiRequest<Document[]>("/documents", { token }),
};
