import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api, CRIME_COLORS } from "@/lib/api";
import { Header } from "./index";

export const Route = createFileRoute("/geospatial")({
  head: () => ({
    meta: [
      { title: "Hotspots Map · KSP Analytics" },
      { name: "description", content: "Geospatial visualisation of crime incidents across Karnataka districts." },
    ],
  }),
  component: GeoSpatial,
});

// Karnataka bbox
const LON_MIN = 74, LON_MAX = 78.6;
const LAT_MIN = 11.5, LAT_MAX = 18.5;

function GeoSpatial() {
  const { data: hotspots = [] } = useQuery({ queryKey: ["hotspots"], queryFn: () => api.hotspots(2000) });
  const allTypes = useMemo(() => Array.from(new Set(hotspots.map((h) => h.type))), [hotspots]);
  const [enabled, setEnabled] = useState<Record<string, boolean>>({});
  const isOn = (t: string) => enabled[t] !== false;

  const filtered = hotspots.filter((h) => isOn(h.type));
  const W = 800, H = 900;
  const project = (lon: number, lat: number) => ({
    cx: ((lon - LON_MIN) / (LON_MAX - LON_MIN)) * W,
    cy: H - ((lat - LAT_MIN) / (LAT_MAX - LAT_MIN)) * H,
  });

  const counts: Record<string, number> = {};
  hotspots.forEach((h) => (counts[h.type] = (counts[h.type] ?? 0) + 1));

  return (
    <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-6">
      <header>
        <div className="text-[11px] uppercase tracking-[0.22em] text-muted-foreground">Geospatial</div>
        <h1 className="mt-2 text-3xl lg:text-4xl font-semibold tracking-tight text-gradient">Crime Hotspots · Karnataka</h1>
        <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
          Geo-tagged incidents projected onto the state extent. Toggle crime categories to isolate spatial patterns.
        </p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        <div className="panel p-3 xl:col-span-3 relative overflow-hidden">
          <div className="absolute inset-0 opacity-30 pointer-events-none"
            style={{ backgroundImage: "radial-gradient(circle at 1px 1px, var(--border) 1px, transparent 0)", backgroundSize: "24px 24px" }} />
          <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-[600px] relative">
            {/* approximate Karnataka outline */}
            <path d="M 220 60 L 360 40 L 470 90 L 560 80 L 640 140 L 680 220 L 720 320 L 700 430 L 660 520 L 600 600 L 540 680 L 470 760 L 380 820 L 300 860 L 240 830 L 200 740 L 160 640 L 130 540 L 110 430 L 130 320 L 170 220 L 200 130 Z"
              fill="color-mix(in oklab, var(--primary) 8%, transparent)"
              stroke="var(--primary)" strokeOpacity={0.5} strokeWidth={1.5} strokeDasharray="4 4" />

            {filtered.map((h, i) => {
              const { cx, cy } = project(h.x, h.y);
              return (
                <circle key={i} cx={cx} cy={cy} r={3} fill={CRIME_COLORS[h.type] ?? "#64748B"} fillOpacity={0.75}>
                  <title>{h.type} — {h.y.toFixed(3)}, {h.x.toFixed(3)}</title>
                </circle>
              );
            })}

            {/* labels */}
            {[
              { name: "Bengaluru", lon: 77.59, lat: 12.97 },
              { name: "Mysuru", lon: 76.65, lat: 12.30 },
              { name: "Mangaluru", lon: 74.85, lat: 12.91 },
              { name: "Hubballi", lon: 75.12, lat: 15.36 },
              { name: "Belagavi", lon: 74.50, lat: 15.85 },
              { name: "Kalaburagi", lon: 76.83, lat: 17.33 },
            ].map((c) => {
              const { cx, cy } = project(c.lon, c.lat);
              return (
                <g key={c.name}>
                  <circle cx={cx} cy={cy} r={5} fill="var(--background)" stroke="var(--foreground)" strokeWidth={1.5} />
                  <text x={cx + 10} y={cy + 4} fontSize={11} fill="var(--foreground)" fontFamily="var(--font-mono)">{c.name}</text>
                </g>
              );
            })}
          </svg>
        </div>

        <div className="space-y-4">
          <div className="panel p-5">
            <Header eyebrow="Layers" title="Crime types" />
            <ul className="mt-3 space-y-1.5">
              {allTypes.map((t) => (
                <li key={t}>
                  <button
                    onClick={() => setEnabled((s) => ({ ...s, [t]: !isOn(t) }))}
                    className={`w-full flex items-center gap-2.5 rounded-md border px-2.5 py-2 text-sm transition-colors ${
                      isOn(t) ? "border-border bg-card/40" : "border-border/40 text-muted-foreground opacity-50"
                    }`}>
                    <span className="size-3 rounded-sm" style={{ background: CRIME_COLORS[t] ?? "#64748B" }} />
                    <span className="flex-1 text-left">{t}</span>
                    <span className="text-xs tabular-nums text-muted-foreground">{counts[t]}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel p-5">
            <Header eyebrow="Coverage" title="On-map stats" />
            <dl className="mt-3 space-y-2 text-sm">
              <Row k="Incidents shown" v={filtered.length.toLocaleString()} />
              <Row k="Total points" v={hotspots.length.toLocaleString()} />
              <Row k="Active layers" v={`${allTypes.filter(isOn).length}/${allTypes.length}`} />
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-muted-foreground">{k}</dt>
      <dd className="tabular-nums">{v}</dd>
    </div>
  );
}
