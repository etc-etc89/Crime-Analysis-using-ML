import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api, CRIME_COLORS, type OverviewStats, type TimelinePoint } from "@/lib/api";
import { KpiCard } from "@/components/kpi-card";
import { BarChart3, Users, Link2, AlertTriangle, ArrowUpRight, MapPin } from "lucide-react";
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from "recharts";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard · KSP Crime Analytics" },
      { name: "description", content: "Executive overview of crime incidents, criminals, associations and ML-detected anomalies across Karnataka." },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: api.stats });
  const { data: timeline } = useQuery({ queryKey: ["timeline"], queryFn: api.timeline });

  const s: OverviewStats | undefined = stats;
  const tl: TimelinePoint[] = timeline ?? [];
  const anomalies = tl.filter((t) => t.isAnomaly).length;
  const total = s?.crime_breakdown.reduce((a, b) => a + b.value, 0) ?? 0;

  return (
    <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Command Console</div>
          <h1 className="mt-2 text-3xl lg:text-4xl font-semibold tracking-tight text-gradient">
            Karnataka State · Crime Intelligence Overview
          </h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
            Live ML-driven aggregation of incidents, criminal profiles, and association graphs across all district commands.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <Pill label="Region" value="All Districts" />
          <Pill label="Window" value="Last 12 months" />
          <Pill label="Model" value="Isolation Forest v3" />
        </div>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Total Incidents" value={(s?.total_incidents ?? 0).toLocaleString()}
          hint={<span className="text-success">▲ 4.2% vs prior period</span>}
          icon={<BarChart3 className="size-5" />} />
        <KpiCard title="Active Criminals" value={(s?.total_criminals ?? 0).toLocaleString()}
          hint={<span className="text-muted-foreground">8.5k profiles indexed</span>}
          icon={<Users className="size-5" />} accent="primary" />
        <KpiCard title="Associations" value={(s?.total_associations ?? 0).toLocaleString()}
          hint={<span className="text-muted-foreground">edges in network graph</span>}
          icon={<Link2 className="size-5" />} accent="warning" />
        <KpiCard title="ML Anomalies" value={anomalies}
          hint={<span className="text-destructive">{anomalies} months above threshold</span>}
          icon={<AlertTriangle className="size-5" />} accent="danger" />
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        <div className="panel p-5 xl:col-span-2 relative overflow-hidden">
          <Header eyebrow="Distribution" title="Crime breakdown" />
          <div className="h-72 mt-2">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={s?.crime_breakdown ?? []} dataKey="value" nameKey="name"
                  innerRadius={60} outerRadius={100} stroke="var(--background)" strokeWidth={2}>
                  {(s?.crime_breakdown ?? []).map((entry) => (
                    <Cell key={entry.name} fill={CRIME_COLORS[entry.name] ?? "#64748B"} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 mt-2 text-xs">
            {(s?.crime_breakdown ?? []).map((c) => (
              <div key={c.name} className="flex items-center gap-2">
                <span className="size-2.5 rounded-sm" style={{ background: CRIME_COLORS[c.name] ?? "#64748B" }} />
                <span className="flex-1 truncate text-muted-foreground">{c.name}</span>
                <span className="tabular-nums">{((c.value / Math.max(total, 1)) * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel p-5 xl:col-span-3">
          <Header eyebrow="Trend · ML overlay" title="Incidents · 24 month window"
            actions={<span className="text-xs text-muted-foreground inline-flex items-center gap-1.5"><span className="size-2 rounded-full bg-destructive" />anomalies</span>} />
          <div className="h-72 mt-2">
            <ResponsiveContainer>
              <AreaChart data={tl}>
                <defs>
                  <linearGradient id="g1" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="incidents" stroke="var(--primary)" strokeWidth={2} fill="url(#g1)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="panel p-5">
          <Header eyebrow="Quick stats" title="Crimes by type" />
          <div className="mt-3 divide-y divide-border">
            {(s?.crime_breakdown ?? []).map((c) => (
              <div key={c.name} className="flex items-center gap-4 py-2.5">
                <span className="size-2.5 rounded-sm shrink-0" style={{ background: CRIME_COLORS[c.name] ?? "#64748B" }} />
                <span className="flex-1 text-sm">{c.name}</span>
                <div className="w-32 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{
                    width: `${(c.value / Math.max(...((s?.crime_breakdown ?? [{ value: 1 }]).map((x) => x.value)))) * 100}%`,
                    background: CRIME_COLORS[c.name] ?? "var(--primary)",
                  }} />
                </div>
                <span className="tabular-nums text-sm w-16 text-right">{c.value.toLocaleString()}</span>
                <span className="tabular-nums text-xs text-muted-foreground w-12 text-right">{((c.value / Math.max(total, 1)) * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel p-5">
          <Header eyebrow="Live feed" title="Recent incidents" actions={
            <button className="text-xs text-primary inline-flex items-center gap-1 hover:underline">View all <ArrowUpRight className="size-3" /></button>
          } />
          <ul className="mt-3 space-y-2">
            {recentIncidents.map((r, i) => (
              <li key={i} className="flex items-center gap-3 rounded-md border border-border/60 bg-card/40 px-3 py-2.5">
                <span className="grid place-items-center size-9 rounded-md border border-border/60" style={{ background: `color-mix(in oklab, ${CRIME_COLORS[r.type] ?? "#64748B"} 20%, transparent)` }}>
                  <MapPin className="size-4" />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm truncate">{r.type} · <span className="text-muted-foreground">{r.location}</span></div>
                  <div className="text-[11px] text-muted-foreground font-mono">{r.id} · {r.time}</div>
                </div>
                <span className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-full border border-border/60 text-muted-foreground">{r.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

function Pill({ label, value }: { label: string; value: string }) {
  return (
    <div className="panel px-3 py-1.5">
      <div className="text-[9px] uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="text-xs font-medium">{value}</div>
    </div>
  );
}

export function Header({ eyebrow, title, actions }: { eyebrow: string; title: string; actions?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{eyebrow}</div>
        <h3 className="text-base font-semibold tracking-tight">{title}</h3>
      </div>
      {actions}
    </div>
  );
}

export function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="panel px-3 py-2 text-xs shadow-xl">
      {label && <div className="text-muted-foreground mb-1">{label}</div>}
      {payload.map((p: any, i: number) => (
        <div key={i} className="flex items-center gap-2">
          <span className="size-2 rounded-sm" style={{ background: p.color || p.payload?.fill }} />
          <span className="text-foreground">{p.name}</span>
          <span className="ml-2 tabular-nums">{typeof p.value === "number" ? p.value.toLocaleString() : p.value}</span>
        </div>
      ))}
    </div>
  );
}

const recentIncidents = [
  { id: "INC-24-08821", type: "Vehicle Theft", location: "Bengaluru South · Jayanagar", time: "12 min ago", status: "Open" },
  { id: "INC-24-08820", type: "Cybercrime", location: "Mangaluru · Hampankatta", time: "37 min ago", status: "Triaged" },
  { id: "INC-24-08819", type: "Fraud", location: "Mysuru · Vijayanagar", time: "1 hr ago", status: "Open" },
  { id: "INC-24-08818", type: "Burglary", location: "Hubballi · Vidyanagar", time: "2 hr ago", status: "Closed" },
  { id: "INC-24-08817", type: "Assault", location: "Belagavi · Camp", time: "3 hr ago", status: "Open" },
  { id: "INC-24-08816", type: "Theft", location: "Davanagere · MCC B Block", time: "4 hr ago", status: "Triaged" },
];
