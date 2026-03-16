import { ReactNode } from "react";

type CardProps = {
  title: string;
  value?: string | number;
  description?: string;
  children?: ReactNode;
};

export function Card({ title, value, description, children }: CardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{title}</p>
      {value !== undefined && (
        <p className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">{value}</p>
      )}
      {description && <p className="mt-2 text-sm text-slate-600">{description}</p>}
      {children}
    </div>
  );
}
