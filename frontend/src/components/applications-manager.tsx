"use client";

import { FormEvent, useEffect, useState } from "react";

import { Table } from "@/components/table";
import { api, Application, JobPosting } from "@/lib/api";
import { getBrowserAuthToken } from "@/lib/client-auth";

export function ApplicationsManager() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [jobId, setJobId] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fitLoading, setFitLoading] = useState(false);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [fitResult, setFitResult] = useState("");
  const [reviewResult, setReviewResult] = useState("");
  const [fitApplicationId, setFitApplicationId] = useState("");
  const [fitProfileContext, setFitProfileContext] = useState("");
  const [fitJobDescription, setFitJobDescription] = useState("");
  const [reviewApplicationId, setReviewApplicationId] = useState("");
  const [reviewResume, setReviewResume] = useState("");
  const [reviewCoverLetter, setReviewCoverLetter] = useState("");
  const [reviewJobDescription, setReviewJobDescription] = useState("");
  const [automationLoading, setAutomationLoading] = useState(false);
  const [automationStatusLoading, setAutomationStatusLoading] = useState(false);
  const [sessionId, setSessionId] = useState("default");
  const [cookieHeader, setCookieHeader] = useState("");
  const [automationJobUrl, setAutomationJobUrl] = useState("");
  const [draftName, setDraftName] = useState("");
  const [draftEmail, setDraftEmail] = useState("");
  const [draftPhone, setDraftPhone] = useState("");
  const [draftCover, setDraftCover] = useState("");
  const [automationTaskId, setAutomationTaskId] = useState("");
  const [automationResult, setAutomationResult] = useState("");

  async function loadData() {
    const token = getBrowserAuthToken();
    if (!token) return;
    try {
      const [apps, jobsList] = await Promise.all([api.applications(token), api.jobs(token)]);
      setApplications(apps);
      setJobs(jobsList);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load data";
      setError(message);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !jobId) return;
    setLoading(true);
    setError("");
    try {
      await api.createApplication(token, {
        job_posting_id: Number(jobId),
        status: "saved",
        notes: notes || undefined,
      });
      setJobId("");
      setNotes("");
      await loadData();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create application";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFitScore(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !fitApplicationId || !fitProfileContext) return;
    setFitLoading(true);
    setError("");
    setFitResult("");
    try {
      const response = await api.fitScore(token, {
        application_id: Number(fitApplicationId),
        profile_context: fitProfileContext,
        job_description: fitJobDescription || undefined,
      });
      setFitResult(response.result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to run fit score";
      setError(message);
    } finally {
      setFitLoading(false);
    }
  }

  async function handleReview(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !reviewApplicationId || !reviewResume || !reviewCoverLetter || !reviewJobDescription)
      return;
    setReviewLoading(true);
    setError("");
    setReviewResult("");
    try {
      const response = await api.reviewApplication(token, {
        application_id: Number(reviewApplicationId),
        resume_text: reviewResume,
        cover_letter: reviewCoverLetter,
        job_description: reviewJobDescription,
      });
      setReviewResult(response.result);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to review application";
      setError(message);
    } finally {
      setReviewLoading(false);
    }
  }

  async function handleBootstrapSession(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !sessionId || !cookieHeader) return;
    setAutomationLoading(true);
    setError("");
    setAutomationResult("");
    try {
      const response = await api.linkedinBootstrapSession(token, {
        session_id: sessionId,
        cookie_header: cookieHeader,
      });
      setAutomationResult(
        `Session bootstrapped: ${response.session_id} (cookies: ${response.cookie_count})`
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to bootstrap session";
      setError(message);
    } finally {
      setAutomationLoading(false);
    }
  }

  async function handleQueueAutomation(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !sessionId || !automationJobUrl) return;
    setAutomationLoading(true);
    setError("");
    setAutomationResult("");
    try {
      const response = await api.linkedinApplyDraft(token, {
        job_url: automationJobUrl,
        session_id: sessionId,
        draft: {
          full_name: draftName || undefined,
          email: draftEmail || undefined,
          phone: draftPhone || undefined,
          cover_letter: draftCover || undefined,
        },
      });
      setAutomationTaskId(response.task_id);
      setAutomationResult(`Task queued: ${response.task_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to queue automation";
      setError(message);
    } finally {
      setAutomationLoading(false);
    }
  }

  async function handleTaskStatus(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token || !automationTaskId) return;
    setAutomationStatusLoading(true);
    setError("");
    try {
      const response = await api.linkedinTaskStatus(token, automationTaskId);
      setAutomationResult(JSON.stringify(response, null, 2));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to fetch task status";
      setError(message);
    } finally {
      setAutomationStatusLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Applications</h1>

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 md:grid-cols-2">
        <select
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
          required
        >
          <option value="">Select a job</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title} - {job.company}
            </option>
          ))}
        </select>
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
        >
          {loading ? "Creating..." : "Create Application"}
        </button>
      </form>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <Table headers={["ID", "Job ID", "Status", "Next Follow-up", "Updated"]}>
        {applications.map((application) => (
          <tr key={application.id} className="text-sm text-slate-700">
            <td className="px-4 py-3 font-medium text-slate-900">#{application.id}</td>
            <td className="px-4 py-3">{application.job_posting_id}</td>
            <td className="px-4 py-3">{application.status}</td>
            <td className="px-4 py-3">{application.next_follow_up_at || "-"}</td>
            <td className="px-4 py-3">{new Date(application.updated_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </Table>

      <div className="grid gap-4 md:grid-cols-2">
        <form onSubmit={handleFitScore} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-semibold tracking-tight">AI Fit Score</h2>
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Application ID"
            value={fitApplicationId}
            onChange={(e) => setFitApplicationId(e.target.value)}
            required
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Profile context"
            value={fitProfileContext}
            onChange={(e) => setFitProfileContext(e.target.value)}
            rows={3}
            required
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Optional job description override"
            value={fitJobDescription}
            onChange={(e) => setFitJobDescription(e.target.value)}
            rows={3}
          />
          <button
            type="submit"
            disabled={fitLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
          >
            {fitLoading ? "Scoring..." : "Run Fit Score"}
          </button>
          {fitResult ? (
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
              {fitResult}
            </pre>
          ) : null}
        </form>

        <form onSubmit={handleReview} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4">
          <h2 className="text-lg font-semibold tracking-tight">AI Application Review</h2>
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Application ID"
            value={reviewApplicationId}
            onChange={(e) => setReviewApplicationId(e.target.value)}
            required
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Resume text"
            value={reviewResume}
            onChange={(e) => setReviewResume(e.target.value)}
            rows={3}
            required
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Cover letter text"
            value={reviewCoverLetter}
            onChange={(e) => setReviewCoverLetter(e.target.value)}
            rows={3}
            required
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Job description"
            value={reviewJobDescription}
            onChange={(e) => setReviewJobDescription(e.target.value)}
            rows={3}
            required
          />
          <button
            type="submit"
            disabled={reviewLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
          >
            {reviewLoading ? "Reviewing..." : "Run Review"}
          </button>
          {reviewResult ? (
            <pre className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
              {reviewResult}
            </pre>
          ) : null}
        </form>
      </div>

      <div className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-4">
        <h2 className="text-lg font-semibold tracking-tight">LinkedIn Automation (Feature Flag)</h2>
        <p className="text-sm text-slate-600">
          Bootstrap a LinkedIn session, queue apply draft prefill, then poll task status.
        </p>

        <form onSubmit={handleBootstrapSession} className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Session ID"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={automationLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
          >
            {automationLoading ? "Saving session..." : "Bootstrap Session"}
          </button>
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            placeholder="Cookie header (e.g., li_at=...; JSESSIONID=...)"
            value={cookieHeader}
            onChange={(e) => setCookieHeader(e.target.value)}
            rows={3}
            required
          />
        </form>

        <form onSubmit={handleQueueAutomation} className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            placeholder="LinkedIn job URL"
            value={automationJobUrl}
            onChange={(e) => setAutomationJobUrl(e.target.value)}
            required
          />
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Full name"
            value={draftName}
            onChange={(e) => setDraftName(e.target.value)}
          />
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Email"
            value={draftEmail}
            onChange={(e) => setDraftEmail(e.target.value)}
          />
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Phone"
            value={draftPhone}
            onChange={(e) => setDraftPhone(e.target.value)}
          />
          <textarea
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2"
            placeholder="Cover letter draft"
            value={draftCover}
            onChange={(e) => setDraftCover(e.target.value)}
            rows={3}
          />
          <button
            type="submit"
            disabled={automationLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
          >
            {automationLoading ? "Queueing..." : "Queue Apply Draft"}
          </button>
        </form>

        <form onSubmit={handleTaskStatus} className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="Task ID"
            value={automationTaskId}
            onChange={(e) => setAutomationTaskId(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={automationStatusLoading}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
          >
            {automationStatusLoading ? "Checking..." : "Check Task Status"}
          </button>
        </form>

        {automationResult ? (
          <pre className="whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
            {automationResult}
          </pre>
        ) : null}
      </div>
    </section>
  );
}
