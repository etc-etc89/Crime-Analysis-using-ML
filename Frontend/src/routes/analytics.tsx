import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Header, ChartTooltip } from "./index";
import {
  ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ReferenceLine,
} from "recharts";
import { AlertTriangle, Brain, Activity } from "lucide-react";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Anomaly Detection · KSP Analytics" },
      { name: "description", content: "ML-based anomaly detection (Isolation Forest) across 24 months of incident data." },
    ],
  }),
  component: Analytics,
});

function Analytics() {
  const { data: timeline = [] } = useQuery({ queryKey: ["timeline"], queryFn: api.timeline });
  const anomalies = [...timeline].filter((t) => t.isAnomaly).sort((a, b) => b.anomalyScore - a.anomalyScore);

  return (
    <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Analytics</div>
        <h1 className="mt-2 text-3xl lg:text-4xl font-semibold tracking-tight text-gradient">Anomaly Detection Timeline</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          Isolation Forest scores each month across multiple dimensions — incident count, dominant crime category, average hour and day-of-week patterns — to surface statistically unusual periods.
        </p>
      </header>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <StatTile icon={<Activity className="size-4" />} label="Months analyzed" value={timeline.length} />
        <StatTile icon={<AlertTriangle className="size-4" />} label="Anomalies detected" value={anomalies.length} accent />
        <StatTile icon={<Brain className="size-4" />} label="Avg anomaly score" value={anomalies.length ? (anomalies.reduce((a, t) => a + t.anomalyScore, 0) / anomalies.length).toFixed(1) : "—"} />
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="panel p-5 xl:col-span-2">
          <Header eyebrow="Timeline" title="Incidents per month" actions={
            <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
              <span className="inline-flex items-center gap-1.5"><span className="size-2 rounded-sm bg-primary" />normal</span>
              <span className="inline-flex items-center gap-1.5"><span className="size-2 rounded-sm bg-destructive" />anomaly</span>
            </div>
          } />
          <div className="h-96 mt-3">
            <ResponsiveContainer>
              <ComposedChart data={timeline}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip content={<AnomalyTooltip />} />
                <ReferenceLine y={150} stroke="var(--warning)" strokeDasharray="4 4" label={{ value: "threshold", fill: "var(--warning)", fontSize: 10, position: "insideTopRight" }} />
                <Bar dataKey="incidents" radius={[4, 4, 0, 0]}>
                  {timeline.map((t, i) => (
                    <Cell key={i} fill={t.isAnomaly ? "var(--destructive)" : "var(--primary)"} fillOpacity={t.isAnomaly ? 0.9 : 0.6} />
                  ))}
                </Bar>
                <Line type="monotone" dataKey="anomalyScore" stroke="var(--warning)" strokeWidth={2} dot={false} yAxisId={0} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-5">
          <Header eyebrow="Most anomalous" title="Top flagged months" />
          <ol className="mt-3 space-y-2">
            {anomalies.slice(0, 6).map((a, i) => (
              <li key={a.date} className="rounded-md border border-border/60 bg-card/40 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="grid place-items-center size-7 rounded-md text-xs font-semibold bg-destructive/20 text-destructive border border-destructive/30">{i + 1}</span>
                    <div>
                      <div className="font-medium text-sm">{a.date}</div>
                      <div className="text-[11px] text-muted-foreground">{a.dominantCrime} dominant</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold tabular-nums">{a.anomalyScore.toFixed(1)}</div>
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground">score</div>
                  </div>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                  <Stat k="Incidents" v={a.incidents} />
                  <Stat k="Avg hour" v={a.avgHour.toFixed(1)} />
                  <Stat k="Avg DOW" v={a.avgDayOfWeek.toFixed(1)} />
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="panel p-5">
        <Header eyebrow="Methodology" title="How anomalies are scored" />
        <p className="mt-2 text-sm text-muted-foreground max-w-3xl">
          The <span className="font-mono text-foreground">Isolation Forest</span> model partitions multi-dimensional feature vectors
          (incident volume, dominant crime category, temporal centroids) and isolates outliers using the average path length across
          random decision trees. Higher scores indicate shorter isolation paths and stronger anomaly signal.
        </p>
      </section>
    </div>
  );
}

function StatTile({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: React.ReactNode; accent?: boolean }) {
  return (
    <div className="panel p-4 flex items-center gap-4">
      <span className={`grid place-items-center size-10 rounded-md border ${accent ? "bg-destructive/15 text-destructive border-destructive/30" : "bg-primary/15 text-primary border-primary/30"}`}>{icon}</span>
      <div>
        <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
        <div className="text-xl font-semibold tabular-nums">{value}</div>
      </div>
    </div>
  );
}

function Stat({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="rounded bg-muted/40 px-2 py-1.5">
      <div className="text-[9px] uppercase tracking-wider text-muted-foreground">{k}</div>
      <div className="tabular-nums">{v}</div>
    </div>
  );
}

function AnomalyTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="panel px-3 py-2 text-xs shadow-xl min-w-[180px]">
      <div className="font-medium">{label}</div>
      <div className="text-muted-foreground mt-1">{p.dominantCrime} dominant</div>
      <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1">
        <span className="text-muted-foreground">Incidents</span><span className="tabular-nums text-right">{p.incidents}</span>
        <span className="text-muted-foreground">Anomaly</span><span className="tabular-nums text-right">{p.anomalyScore.toFixed(1)}</span>
        <span className="text-muted-foreground">Avg hour</span><span className="tabular-nums text-right">{p.avgHour.toFixed(1)}</span>
        <span className="text-muted-foreground">Avg DOW</span><span className="tabular-nums text-right">{p.avgDayOfWeek.toFixed(1)}</span>
      </div>
      {p.isAnomaly && <div className="mt-2 text-destructive text-[10px] uppercase tracking-wider">⚠ flagged anomaly</div>}
    </div>
  );
}
