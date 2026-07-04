import { Link, useRouterState } from "@tanstack/react-router";
import { LayoutDashboard, Activity, Map, Network, Search, Shield } from "lucide-react";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analytics", label: "Anomalies", icon: Activity },
  { to: "/geospatial", label: "Hotspots", icon: Map },
  { to: "/network", label: "Network", icon: Network },
  { to: "/criminals", label: "Criminals", icon: Search },
] as const;

export function AppSidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-xl">
      <div className="flex items-center gap-3 px-6 py-6 border-b border-border">
        <div className="grid place-items-center size-10 rounded-md bg-primary/15 text-primary border border-primary/30">
          <Shield className="size-5" />
        </div>
        <div className="leading-tight">
          <div className="font-semibold tracking-tight">KSP Analytics</div>
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">Datathon 2026</div>
        </div>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {nav.map(({ to, label, icon: Icon }) => {
          const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
          return (
            <Link
              key={to}
              to={to}
              className={[
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors",
                active
                  ? "bg-primary/15 text-foreground border border-primary/30"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              ].join(" ")}
            >
              <Icon className="size-4" />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border text-[11px] text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-success animate-pulse" />
          Live feed · classified
        </div>
      </div>
    </aside>
  );
}

export function MobileNav() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <nav className="lg:hidden sticky top-0 z-30 flex overflow-x-auto gap-1 bg-card/80 backdrop-blur border-b border-border px-2 py-2">
      {nav.map(({ to, label, icon: Icon }) => {
        const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
        return (
          <Link key={to} to={to} className={[
            "flex items-center gap-2 rounded-md px-3 py-2 text-xs whitespace-nowrap",
            active ? "bg-primary/15 text-foreground" : "text-muted-foreground"
          ].join(" ")}>
            <Icon className="size-4" />{label}
          </Link>
        );
      })}
    </nav>
  );
}
