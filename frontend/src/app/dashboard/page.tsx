import { redirect } from "next/navigation";

import { Card } from "@/components/ui/card";
import { getServerAuthToken } from "@/lib/auth";
import { api } from "@/lib/api";

export default async function DashboardPage() {
  const token = getServerAuthToken();
  if (!token) {
    redirect("/login");
  }

  const metrics = await api.metrics(token).catch(() => ({
    total_applications: 0,
    applied_count: 0,
    interview_count: 0,
    response_rate: 0,
    pending_follow_ups: 0,
  }));

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Application Dashboard</h1>
        <p className="mt-1 text-sm text-slate-600">
          Minimal overview of pipeline health, follow-ups, and interview momentum.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card title="Total" value={metrics.total_applications} />
        <Card title="Applied" value={metrics.applied_count} />
        <Card title="Interviews" value={metrics.interview_count} />
        <Card title="Response Rate" value={`${(metrics.response_rate * 100).toFixed(0)}%`} />
        <Card title="Pending Follow-ups" value={metrics.pending_follow_ups} />
      </div>
    </section>
  );
}
