import { redirect } from "next/navigation";

import { Table } from "@/components/table";
import { getServerAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";

export default async function ApplicationsPage() {
  const token = getServerAuthToken();
  if (!token) {
    redirect("/login");
  }
  const applications = await api.applications(token).catch(() => []);

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Applications</h1>
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
