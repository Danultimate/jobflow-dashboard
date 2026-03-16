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
    </section>
  );
}
