"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/",       label: "Overview" },
  { href: "/runs",   label: "Runs" },
  { href: "/alerts", label: "Alerts" },
  { href: "/trend",  label: "Trend" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-44 flex-col border-r border-[var(--border)] bg-[var(--surface)] px-3 py-5 sticky top-0">
      <div className="mb-8 px-2">
        <span className="text-lg font-bold text-veld-400">🌾 Veldwatch</span>
      </div>
      <nav className="space-y-1">
        {NAV.map(({ href, label }) => {
          const active =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`block rounded px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-veld-900 text-veld-300 font-semibold"
                  : "text-[var(--muted)] hover:text-[var(--text)] hover:bg-[var(--border)]"
              }`}
            >
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto px-2 text-xs text-[var(--muted)]">v0.1.0</div>
    </aside>
  );
}
