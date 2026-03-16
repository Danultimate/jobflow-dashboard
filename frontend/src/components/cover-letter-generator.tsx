"use client";

import { FormEvent, useEffect, useState } from "react";

import { Table } from "@/components/table";
import { api, Document } from "@/lib/api";
import { getBrowserAuthToken } from "@/lib/client-auth";

type CoverLetterForm = {
  application_id: string;
  profile_context: string;
  company: string;
  role: string;
  job_description: string;
};

const initialForm: CoverLetterForm = {
  application_id: "",
  profile_context: "",
  company: "",
  role: "",
  job_description: "",
};

export function CoverLetterGenerator() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [form, setForm] = useState<CoverLetterForm>(initialForm);
  const [generatedText, setGeneratedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDocuments() {
    const token = getBrowserAuthToken();
    if (!token) return;
    try {
      const docs = await api.documents(token);
      setDocuments(docs);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load documents";
      setError(message);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const token = getBrowserAuthToken();
    if (!token) return;
    setLoading(true);
    setError("");
    setGeneratedText("");
    try {
      const result = await api.generateCoverLetter(token, {
        application_id: Number(form.application_id),
        profile_context: form.profile_context,
        company: form.company,
        role: form.role,
        job_description: form.job_description,
      });
      setGeneratedText(result.content ?? "");
      await loadDocuments();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to generate cover letter";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
      <p className="text-sm text-slate-600">Generate and version cover letters with Ollama.</p>

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4">
        <input
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Application ID"
          value={form.application_id}
          onChange={(e) => setForm((prev) => ({ ...prev, application_id: e.target.value }))}
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
          placeholder="Role"
          value={form.role}
          onChange={(e) => setForm((prev) => ({ ...prev, role: e.target.value }))}
          required
        />
        <textarea
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Profile context"
          value={form.profile_context}
          onChange={(e) => setForm((prev) => ({ ...prev, profile_context: e.target.value }))}
          rows={3}
          required
        />
        <textarea
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          placeholder="Job description"
          value={form.job_description}
          onChange={(e) => setForm((prev) => ({ ...prev, job_description: e.target.value }))}
          rows={4}
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60 md:w-fit"
        >
          {loading ? "Generating..." : "Generate Cover Letter"}
        </button>
      </form>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {generatedText ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <p className="mb-2 text-sm font-medium text-slate-700">Latest generated text</p>
          <pre className="whitespace-pre-wrap text-sm text-slate-700">{generatedText}</pre>
        </div>
      ) : null}

      <Table headers={["Title", "Kind", "Application", "Version", "Created"]}>
        {documents.map((document) => (
          <tr key={document.id} className="text-sm text-slate-700">
            <td className="px-4 py-3 font-medium text-slate-900">{document.title}</td>
            <td className="px-4 py-3">{document.kind}</td>
            <td className="px-4 py-3">#{document.application_id}</td>
            <td className="px-4 py-3">v{document.version}</td>
            <td className="px-4 py-3">{new Date(document.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </Table>
    </section>
  );
}
