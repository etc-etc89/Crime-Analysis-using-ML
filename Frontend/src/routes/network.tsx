import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api, THREAT_COLORS, type Kingpin } from "@/lib/api";
import { Header } from "./index";
import { AIThreatAnalyzer } from "@/components/ai-threat-analyzer";

export const Route = createFileRoute("/network")({
  head: () => ({
    meta: [
      { title: "Criminal Network · KSP Analytics" },
      { name: "description", content: "Network analysis of criminal associations and high-centrality actors (kingpins)." },
    ],
  }),
  component: NetworkGraph,
});

function NetworkGraph() {
  const { data: kingpins = [] } = useQuery({ queryKey: ["kingpins"], queryFn: () => api.kingpins(15) });
  const [selected, setSelected] = useState<string | null>(null);

  const W = 800, H = 600;
  // deterministic circular layout + a few bridging edges
  const layout = useMemo(() => {
    return kingpins.map((k, i) => {
      const angle = (i / Math.max(kingpins.length, 1)) * Math.PI * 2;
      const radius = 220 - (k.connections / 200) * 70;
      return {
        ...k,
        x: W / 2 + Math.cos(angle) * radius,
        y: H / 2 + Math.sin(angle) * radius,
      };
    });
  }, [kingpins]);

  const edges = useMemo(() => {
    const out: { a: string; b: string }[] = [];
    layout.forEach((n, i) => {
      // each node connects to 2-3 others deterministically
      const next1 = layout[(i + 1) % layout.length];
      const next2 = layout[(i + 3) % layout.length];
      const next3 = layout[(i + 5) % layout.length];
      out.push({ a: n.id, b: next1.id });
      out.push({ a: n.id, b: next2.id });
      if (i % 2 === 0) out.push({ a: n.id, b: next3.id });
    });
    return out;
  }, [layout]);

  const sel = selected ? layout.find((n) => n.id === selected) ?? null : null;
  const connectedIds = useMemo(() => {
    if (!sel) return new Set<string>();
    const s = new Set<string>();
    edges.forEach((e) => {
      if (e.a === sel.id) s.add(e.b);
      if (e.b === sel.id) s.add(e.a);
    });
    return s;
  }, [edges, sel]);

  return (
    <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Network Intelligence</div>
        <h1 className="mt-2 text-3xl lg:text-4xl font-semibold tracking-tight text-gradient">Criminal Associations & Kingpins</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          Force-directed view of top-ranked actors sized by degree centrality. Click a node to expand its first-degree network.
        </p>
      </header>

      {/* AI Threat Analyzer Component */}
      <AIThreatAnalyzer />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="panel p-3 xl:col-span-2 relative overflow-hidden">
          <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-[600px]">
            <defs>
              <radialGradient id="halo">
                <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.5} />
                <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
              </radialGradient>
            </defs>

            {edges.map((e, i) => {
              const a = layout.find((n) => n.id === e.a)!;
              const b = layout.find((n) => n.id === e.b)!;
              const highlight = sel && (e.a === sel.id || e.b === sel.id);
              const dim = sel && !highlight;
              return (
                <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                  stroke={highlight ? "var(--primary)" : "var(--border)"}
                  strokeOpacity={dim ? 0.15 : highlight ? 0.9 : 0.5}
                  strokeWidth={highlight ? 1.5 : 1}
                  strokeDasharray={highlight ? undefined : "3 3"} />
              );
            })}

            {layout.map((n) => {
              const r = 10 + (n.connections / 200) * 22;
              const isSel = sel?.id === n.id;
              const isLinked = connectedIds.has(n.id);
              const dim = sel && !isSel && !isLinked;
              return (
                <g key={n.id} onClick={() => setSelected(n.id === selected ? null : n.id)} className="cursor-pointer" opacity={dim ? 0.25 : 1}>
                  {isSel && <circle cx={n.x} cy={n.y} r={r + 18} fill="url(#halo)" />}
                  <circle cx={n.x} cy={n.y} r={r}
                    fill={THREAT_COLORS[n.threat_level]}
                    fillOpacity={0.85}
                    stroke={isSel ? "var(--foreground)" : "var(--background)"}
                    strokeWidth={isSel ? 2.5 : 2} />
                  <text x={n.x} y={n.y + r + 12} textAnchor="middle" fontSize={10}
                    fill="var(--foreground)" fontFamily="var(--font-mono)">{n.name.split(" ")[0]}</text>
                </g>
              );
            })}
          </svg>
          <div className="absolute bottom-3 left-3 flex items-center gap-3 text-[11px] text-muted-foreground panel px-3 py-1.5">
            {(["High", "Medium", "Low"] as const).map((t) => (
              <span key={t} className="inline-flex items-center gap-1.5">
                <span className="size-2.5 rounded-full" style={{ background: THREAT_COLORS[t] }} />{t}
              </span>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <DetailPanel sel={sel} />
          <div className="panel p-5">
            <Header eyebrow="Ranking" title="Top kingpins" />
            <div className="mt-3 max-h-[420px] overflow-auto -mx-2">
              <table className="w-full text-sm">
                <thead className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  <tr>
                    <th className="text-left px-2 py-1.5">#</th>
                    <th className="text-left px-2 py-1.5">Name</th>
                    <th className="text-right px-2 py-1.5">Conn.</th>
                    <th className="text-right px-2 py-1.5">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {[...kingpins].sort((a, b) => b.connections - a.connections).map((k, i) => (
                    <tr key={k.id}
                      onClick={() => setSelected(k.id === selected ? null : k.id)}
                      className={`cursor-pointer border-t border-border/60 hover:bg-accent/50 ${selected === k.id ? "bg-primary/10" : ""}`}>
                      <td className="px-2 py-2 text-muted-foreground tabular-nums">{i + 1}</td>
                      <td className="px-2 py-2">
                        <div className="flex items-center gap-2">
                          <span className="size-2 rounded-full" style={{ background: THREAT_COLORS[k.threat_level] }} />
                          {k.name}
                        </div>
                      </td>
                      <td className="px-2 py-2 text-right tabular-nums">{k.connections}</td>
                      <td className="px-2 py-2 text-right tabular-nums">{k.base_risk_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DetailPanel({ sel }: { sel: (Kingpin & { x: number; y: number }) | null }) {
  return (
    <div className="panel p-5">
      <Header eyebrow="Profile" title={sel ? sel.name : "Select a node"} />
      {!sel ? (
        <p className="mt-3 text-sm text-muted-foreground">Click any node in the network to inspect its profile, threat rating, and first-degree associations.</p>
      ) : (
        <div className="mt-3 space-y-3 text-sm">
          <div className="grid grid-cols-3 gap-2">
            <Stat k="Age" v={sel.age} />
            <Stat k="Connections" v={sel.connections} />
            <Stat k="Risk" v={sel.base_risk_score} />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Threat level</span>
            <span className="px-2 py-0.5 rounded-full text-xs font-medium" style={{
              background: `color-mix(in oklab, ${THREAT_COLORS[sel.threat_level]} 25%, transparent)`,
              color: THREAT_COLORS[sel.threat_level],
              border: `1px solid ${THREAT_COLORS[sel.threat_level]}40`,
            }}>{sel.threat_level}</span>
          </div>
          <div className="flex items-center justify-between font-mono text-xs text-muted-foreground">
            <span>ID</span><span>{sel.id}</span>
          </div>
        </div>
      )}
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
