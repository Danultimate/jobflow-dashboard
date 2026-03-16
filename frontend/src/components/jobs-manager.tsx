"use client";

import { FormEvent, useEffect, useState } from "react";

import { Table } from "@/components/table";
import { api, JobPosting } from "@/lib/api";
import { getBrowserAuthToken } from "@/lib/client-auth";

type JobForm = {
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
};

const initialForm: JobForm = {
  title: "",
  company: "",
  location: "",
  description: "",
  url: "",
};

export function JobsManager() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [form, setForm] = useState<JobForm>(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadJobs() {
    const token = getBrowserAuthToken();
    if (!token) return;
    try {
      const data = await api.jobs(token);
      setJobs(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load jobs";
      setError(message);
    }
  }

  useEffect(() => {
    void loadJobs();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      await api.importJob(token, {
        source: "linkedin_manual",
        title: form.title,
        company: form.company,
        location: form.location || undefined,
        description: form.description || undefined,
        url: form.url || undefined,
      });
      setForm(initialForm);
      await loadJobs();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to import job";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
        <p className="text-sm text-slate-600">Add LinkedIn jobs manually and track them instantly.</p>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 md:grid-cols-2">
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Job title"
          value={form.title}
          onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          required
        />
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Company"
          value={form.company}
          onChange={(e) => setForm((prev) => ({ ...prev, company: e.target.value }))}
          required
        />
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Location"
          value={form.location}
          onChange={(e) => setForm((prev) => ({ ...prev, location: e.target.value }))}
        />
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="LinkedIn URL"
          value={form.url}
          onChange={(e) => setForm((prev) => ({ ...prev, url: e.target.value }))}
        />
        <textarea
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-2"
          placeholder="Short description"
          value={form.description}
          onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          rows={3}
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
        >
          {loading ? "Adding..." : "Add Job"}
        </button>
      </form>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <Table headers={["Title", "Company", "Location", "Source"]}>
        {jobs.map((job) => (
          <tr key={job.id} className="text-sm text-slate-700">
            <td className="px-4 py-3 font-medium text-slate-900">{job.title}</td>
            <td className="px-4 py-3">{job.company}</td>
            <td className="px-4 py-3">{job.location || "-"}</td>
            <td className="px-4 py-3">{job.source}</td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
