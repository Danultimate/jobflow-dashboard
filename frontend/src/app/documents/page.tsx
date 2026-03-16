import { redirect } from "next/navigation";

import { Table } from "@/components/table";
import { getServerAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";

export default async function DocumentsPage() {
  const token = getServerAuthToken();
  if (!token) {
    redirect("/login");
  }
  const documents = await api.documents(token).catch(() => []);

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-semibold tracking-tight">Documents</h1>
      <p className="text-sm text-slate-600">
        Generated artifacts (cover letters, notes, and review outputs) with version tracking.
      </p>
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
