// Centralized API + mock fallback so the UI is fully functional even if the
// FastAPI backend at localhost:8000 isn't reachable from the deployed preview.

export const API_BASE =
  (typeof window !== "undefined" && (window as any).__KSP_API__) ||
  (import.meta.env.VITE_KSP_API as string | undefined) ||
  "http://localhost:8000";

export interface OverviewStats {
  total_incidents: number;
  total_criminals: number;
  total_associations: number;
  crime_breakdown: { name: string; value: number }[];
}

export interface TimelinePoint {
  date: string;
  incidents: number;
  isAnomaly: boolean;
  anomalyScore: number;
  avgDayOfWeek: number;
  avgHour: number;
  dominantCrime: string;
}

export interface Hotspot { x: number; y: number; type: string }

export interface Kingpin {
  id: string;
  name: string;
  age: number;
  base_risk_score: number;
  threat_level: "Low" | "Medium" | "High";
  connections: number;
}

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { signal: AbortSignal.timeout(2500) });
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

// ---------- Mock data ----------
const CRIME_TYPES = ["Vehicle Theft", "Fraud", "Murder", "Theft", "Cybercrime", "Assault", "Burglary"];

const mockStats: OverviewStats = {
  total_incidents: 15243,
  total_criminals: 8517,
  total_associations: 12089,
  crime_breakdown: [
    { name: "Theft", value: 6450 },
    { name: "Vehicle Theft", value: 4500 },
    { name: "Fraud", value: 3200 },
    { name: "Cybercrime", value: 2100 },
    { name: "Burglary", value: 1450 },
    { name: "Assault", value: 980 },
    { name: "Murder", value: 850 },
  ],
};

function seeded(i: number) { const s = Math.sin(i * 9301 + 49297) * 233280; return s - Math.floor(s); }

const mockTimeline: TimelinePoint[] = Array.from({ length: 24 }, (_, i) => {
  const year = 2023 + Math.floor(i / 12);
  const month = String((i % 12) + 1).padStart(2, "0");
  const base = 110 + Math.round(seeded(i) * 60);
  const spike = [3, 9, 14, 20].includes(i);
  const incidents = spike ? base + 80 + Math.round(seeded(i + 1) * 40) : base;
  return {
    date: `${year}-${month}`,
    incidents,
    isAnomaly: spike,
    anomalyScore: spike ? 70 + seeded(i + 2) * 25 : seeded(i + 3) * 40,
    avgDayOfWeek: 2 + seeded(i + 4) * 4,
    avgHour: 8 + seeded(i + 5) * 14,
    dominantCrime: CRIME_TYPES[i % CRIME_TYPES.length],
  };
});

// Karnataka bbox approx: lon 74-78.5, lat 11.5-18.5
const mockHotspots: Hotspot[] = Array.from({ length: 600 }, (_, i) => ({
  x: 74 + seeded(i) * 4.5,
  y: 11.5 + seeded(i + 100) * 7,
  type: CRIME_TYPES[Math.floor(seeded(i + 200) * CRIME_TYPES.length)],
}));

const NAMES = [
  "Manan Shankar", "Arjun Rao", "Vikram Naidu", "Rohit Hegde", "Suresh Kamath",
  "Pradeep Iyer", "Kiran Murthy", "Aditya Pillai", "Naveen Reddy", "Sandeep Gowda",
  "Harish Bhat", "Yogesh Kulkarni", "Mahesh Acharya", "Dinesh Shetty", "Anil Patil",
];

const mockKingpins: Kingpin[] = NAMES.map((name, i) => {
  const conns = 140 - i * 8 + Math.round(seeded(i) * 10);
  const score = 90 - i * 4 + Math.round(seeded(i + 1) * 8);
  const threat: Kingpin["threat_level"] = score > 70 ? "High" : score > 45 ? "Medium" : "Low";
  return {
    id: `crim-${String(i + 1).padStart(4, "0")}`,
    name,
    age: 28 + Math.round(seeded(i + 2) * 30),
    base_risk_score: score,
    threat_level: threat,
    connections: conns,
  };
});

// ---------- Public API ----------
export const api = {
  stats: () => fetchJson<OverviewStats>("/api/v1/overview/stats", mockStats),
  timeline: () => fetchJson<TimelinePoint[]>("/api/v1/analytics/timeline", mockTimeline),
  hotspots: (limit = 2000) =>
    fetchJson<Hotspot[]>(`/api/v1/geospatial/hotspots?limit=${limit}`, mockHotspots),
  kingpins: (topN = 15) =>
    fetchJson<Kingpin[]>(`/api/v1/network/kingpins?top_n=${topN}`, mockKingpins),
};

export const CRIME_COLORS: Record<string, string> = {
  "Vehicle Theft": "#EF4444",
  "Fraud": "#F59E0B",
  "Murder": "#991B1B",
  "Theft": "#F97316",
  "Cybercrime": "#6366F1",
  "Assault": "#EC4899",
  "Burglary": "#8B5CF6",
};

export const THREAT_COLORS: Record<Kingpin["threat_level"], string> = {
  Low: "#10B981",
  Medium: "#F59E0B",
  High: "#EF4444",
};
