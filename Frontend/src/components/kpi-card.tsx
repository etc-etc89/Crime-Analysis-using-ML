import type { ReactNode } from "react";

export function KpiCard({
  title, value, hint, icon, accent = "primary",
}: {
  title: string;
  value: string | number;
  hint?: ReactNode;
  icon: ReactNode;
  accent?: "primary" | "danger" | "warning" | "success";
}) {
  const accentClass = {
    primary: "from-primary/25 to-transparent text-primary",
    danger: "from-destructive/25 to-transparent text-destructive",
    warning: "from-warning/25 to-transparent",
    success: "from-success/25 to-transparent text-success",
  }[accent];

  return (
    <div className="panel panel-glow p-5 relative overflow-hidden">
      <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r ${accentClass}`} />
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{title}</div>
          <div className="mt-2 text-3xl font-semibold tabular-nums text-gradient">{value}</div>
          {hint && <div className="mt-1.5 text-xs text-muted-foreground">{hint}</div>}
        </div>
        <div className={`grid place-items-center size-10 rounded-md bg-gradient-to-b ${accentClass} border border-border/60`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
