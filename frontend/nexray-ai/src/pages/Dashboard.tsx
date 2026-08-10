// ============================================================
// NexRay AI - Dashboard
// Connected to real backend stats.
// ============================================================

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScanLine, Stethoscope, FileText, Activity } from "lucide-react";
import { getToken, getDoctor } from "@/lib/api";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";

interface Stats {
  xray_count: number;
  symptom_count: number;
  report_count: number;
  activity: { day: string; analyses: number; symptoms: number }[];
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const doctor = getDoctor();

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      const res = await fetch("http://localhost:8000/reports/stats", {
        headers: {
          "Authorization": `Bearer ${getToken()}`,
        },
      });
      if (!res.ok) throw new Error("Failed to fetch stats");
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Stats fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }

  const statCards = [
    {
      label: "X-Ray Analyses this week",
      value: stats?.xray_count ?? 0,
      icon: ScanLine,
    },
    {
      label: "Symptom checks this week",
      value: stats?.symptom_count ?? 0,
      icon: Stethoscope,
    },
    {
      label: "Reports generated",
      value: stats?.report_count ?? 0,
      icon: FileText,
    },
    {
      label: "Model uptime",
      value: "99.9%",
      icon: Activity,
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Welcome */}
      <div>
        <h1 className="text-page-title text-text-primary">
          Welcome back, {doctor?.name ?? "Doctor"}
        </h1>
        <p className="text-body text-text-secondary mt-1">
          Here's what's happening across your workspace today.
        </p>
      </div>

      {/* Stat cards */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="py-6">
                <div className="h-8 w-16 rounded bg-surface-secondary animate-pulse mb-2" />
                <div className="h-4 w-28 rounded bg-surface-secondary animate-pulse" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map(({ label, value, icon: Icon }) => (
            <Card key={label}>
              <CardContent className="flex items-center justify-between py-6">
                <div>
                  <p className="text-tiny text-text-secondary uppercase tracking-wide">{label}</p>
                  <p className="text-3xl font-bold text-text-primary mt-1">{value}</p>
                </div>
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Icon size={22} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Weekly activity chart */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly activity</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="h-48 w-full rounded bg-surface-secondary animate-pulse" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={stats?.activity ?? []} margin={{ top: 8, right: 16, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="analyses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1A3C5E" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#1A3C5E" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="symptoms" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2E86AB" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2E86AB" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="analyses"
                  stroke="#1A3C5E"
                  fillOpacity={1}
                  fill="url(#analyses)"
                  name="X-Ray Analyses"
                />
                <Area
                  type="monotone"
                  dataKey="symptoms"
                  stroke="#2E86AB"
                  fillOpacity={1}
                  fill="url(#symptoms)"
                  name="Symptom Checks"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}