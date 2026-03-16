"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/jobs", label: "Jobs" },
  { href: "/applications", label: "Applications" },
  { href: "/documents", label: "Documents" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  if (pathname === "/login") {
    return null;
  }

  function logout() {
    document.cookie = "jobflow_token=; path=/; max-age=0; samesite=lax";
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="container-shell flex items-center justify-between py-4">
        <Link href="/dashboard" className="text-sm font-semibold tracking-wide text-slate-900">
          JobFlow
        </Link>
        <nav className="flex gap-5">
          {links.map((link) => (
            <Link key={link.href} href={link.href} className="text-sm text-slate-600 hover:text-slate-900">
              {link.label}
            </Link>
          ))}
          <button
            onClick={logout}
            className="text-sm text-slate-500 hover:text-slate-900"
            type="button"
          >
            Logout
          </button>
        </nav>
      </div>
    </header>
  );
}
