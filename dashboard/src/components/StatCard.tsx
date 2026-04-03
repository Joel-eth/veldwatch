interface Props {
  label: string;
  value: number;
  variant?: "default" | "success" | "danger" | "info";
}

const VARIANTS = {
  default: "text-[var(--text)]",
  success: "text-veld-400",
  danger:  "text-red-400",
  info:    "text-blue-400",
};

export function StatCard({ label, value, variant = "default" }: Props) {
  return (
    <div className="card flex flex-col gap-1">
      <span className="text-xs text-[var(--muted)] uppercase tracking-widest">{label}</span>
      <span className={`text-3xl font-bold font-mono ${VARIANTS[variant]}`}>{value}</span>
    </div>
  );
}
