import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api, THREAT_COLORS, type Kingpin } from "@/lib/api";
import { Header } from "./index";
import { Search } from "lucide-react";

export const Route = createFileRoute("/criminals")({
  head: () => ({
    meta: [
      { title: "Criminal Database · KSP Analytics" },
      { name: "description", content: "Full-text criminal database search with threat filters and detailed profile inspection." },
    ],
  }),
  component: CriminalSearch,
});

function CriminalSearch() {
  const { data: kingpins = [] } = useQuery({ queryKey: ["kingpins"], queryFn: () => api.kingpins(15) });
  const [q, setQ] = useState("");
  const [threat, setThreat] = useState<"all" | Kingpin["threat_level"]>("all");
  const [sortKey, setSortKey] = useState<keyof Kingpin>("base_risk_score");
  const [selected, setSelected] = useState<Kingpin | null>(null);

  const rows = useMemo(() => {
    return kingpins
      .filter((k) => threat === "all" || k.threat_level === threat)
      .filter((k) => !q || k.name.toLowerCase().includes(q.toLowerCase()) || k.id.includes(q))
      .sort((a, b) => (b[sortKey] as number) - (a[sortKey] as number));
  }, [kingpins, q, threat, sortKey]);

  return (
    <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Database</div>
        <h1 className="mt-2 text-3xl lg:text-4xl font-semibold tracking-tight text-gradient">Criminal Search & Profiles</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          Filter by threat level, sort by risk or association density, and open detailed dossiers.
        </p>
      </header>

      <div className="panel p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            value={q} onChange={(e) => setQ(e.target.value)}
            placeholder="Search name or ID…"
            className="w-full bg-muted/40 border border-border rounded-md pl-9 pr-3 py-2 text-sm outline-none focus:border-primary"
          />
        </div>
        <div className="flex items-center gap-1 text-xs">
          {(["all", "High", "Medium", "Low"] as const).map((t) => (
            <button key={t} onClick={() => setThreat(t)}
              className={`px-3 py-1.5 rounded-md border ${threat === t ? "bg-primary/15 text-foreground border-primary/40" : "border-border text-muted-foreground hover:text-foreground"}`}>
              {t === "all" ? "All" : t}
            </button>
          ))}
        </div>
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value as keyof Kingpin)}
          className="bg-muted/40 border border-border rounded-md px-3 py-2 text-sm outline-none">
          <option value="base_risk_score">Sort: Risk Score</option>
          <option value="connections">Sort: Connections</option>
          <option value="age">Sort: Age</option>
        </select>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="panel xl:col-span-2 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="text-[10px] uppercase tracking-wider text-muted-foreground bg-card/60">
              <tr>
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">ID</th>
                <th className="text-right px-4 py-3">Age</th>
                <th className="text-right px-4 py-3">Connections</th>
                <th className="text-right px-4 py-3">Risk</th>
                <th className="text-left px-4 py-3">Threat</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((k) => (
                <tr key={k.id}
                  onClick={() => setSelected(k)}
                  className={`cursor-pointer border-t border-border/60 hover:bg-accent/50 ${selected?.id === k.id ? "bg-primary/10" : ""}`}>
                  <td className="px-4 py-3 font-medium">{k.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{k.id}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{k.age}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{k.connections}</td>
                  <td className="px-4 py-3 text-right tabular-nums font-semibold">{k.base_risk_score}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider" style={{
                      background: `color-mix(in oklab, ${THREAT_COLORS[k.threat_level]} 22%, transparent)`,
                      color: THREAT_COLORS[k.threat_level],
                      border: `1px solid ${THREAT_COLORS[k.threat_level]}40`,
                    }}>{k.threat_level}</span>
                  </td>
                </tr>
              ))}
              {!rows.length && (
                <tr><td colSpan={6} className="px-4 py-10 text-center text-muted-foreground text-sm">No matches.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <aside className="panel p-5 h-fit sticky top-4">
          <Header eyebrow="Dossier" title={selected?.name ?? "Select a record"} />
          {!selected ? (
            <p className="mt-3 text-sm text-muted-foreground">Click a row to load the criminal's profile, key metrics, and risk assessment.</p>
          ) : (
            <div className="mt-4 space-y-4">
              <div className="flex items-center gap-4">
                <div className="size-16 rounded-md border border-border bg-gradient-to-br from-muted to-card grid place-items-center text-2xl font-semibold text-muted-foreground">
                  {selected.name.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <div className="font-semibold text-lg">{selected.name}</div>
                  <div className="text-xs font-mono text-muted-foreground">{selected.id}</div>
                  <div className="mt-1 inline-block px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider" style={{
                    background: `color-mix(in oklab, ${THREAT_COLORS[selected.threat_level]} 22%, transparent)`,
                    color: THREAT_COLORS[selected.threat_level],
                    border: `1px solid ${THREAT_COLORS[selected.threat_level]}40`,
                  }}>{selected.threat_level} threat</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 text-sm">
                <Metric k="Age" v={selected.age} />
                <Metric k="Connections" v={selected.connections} />
                <Metric k="Risk" v={selected.base_risk_score} />
              </div>

              <div>
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">Risk profile</div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full" style={{
                    width: `${selected.base_risk_score}%`,
                    background: `linear-gradient(90deg, ${THREAT_COLORS.Low}, ${THREAT_COLORS.Medium}, ${THREAT_COLORS.High})`,
                  }} />
                </div>
              </div>

              <div className="text-xs text-muted-foreground">
                Cross-references {selected.connections} associates across organized theft, fraud, and cyber units. Subject is active in 3 districts with elevated nighttime activity.
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

function Metric({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="rounded-md border border-border/60 bg-muted/40 px-3 py-2">
      <div className="text-[9px] uppercase tracking-wider text-muted-foreground">{k}</div>
      <div className="text-lg font-semibold tabular-nums">{v}</div>
    </div>
  );
}
