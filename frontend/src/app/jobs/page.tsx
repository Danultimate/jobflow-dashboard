import { redirect } from "next/navigation";

import { Table } from "@/components/table";
import { getServerAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";

export default async function JobsPage() {
  const token = getServerAuthToken();
  if (!token) {
    redirect("/login");
  }
  const jobs = await api.jobs(token).catch(() => []);

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Jobs</h1>
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
