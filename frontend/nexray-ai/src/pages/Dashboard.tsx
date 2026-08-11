// ============================================================
// NexRay AI - Dashboard
// Mobile optimised layout with real backend stats.
// ============================================================

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScanLine, Stethoscope, FileText, Activity, GitMerge } from "lucide-react";
import { getDoctor, getStats } from "@/lib/api";
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
  combined_count: number;
  report_count: number;
  activity: { day: string; analyses: number; symptoms: number; combined: number }[];
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const doctor = getDoctor();
  const firstName = doctor?.name?.split(" ")[0] ?? "Doctor";

  useEffect(() => {
    fetchStats();
  }, []);

  async function fetchStats() {
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      console.error("Stats fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }

  const statCards = [
    {
      label: "X-Ray Analyses",
      sublabel: "this week",
      value: stats?.xray_count ?? 0,
      icon: ScanLine,
    },
    {
      label: "Symptom Checks",
      sublabel: "this week",
      value: stats?.symptom_count ?? 0,
      icon: Stethoscope,
    },
    {
      label: "Combined Cases",
      sublabel: "this week",
      value: stats?.combined_count ?? 0,
      icon: GitMerge,
    },
    {
      label: "Reports",
      sublabel: "generated",
      value: stats?.report_count ?? 0,
      icon: FileText,
    },
  ];

  return (
    <div className="flex flex-col gap-4 p-1">
      <div>
        <h1 className="text-2xl font-bold text-text-primary leading-tight">
          Welcome back, {firstName}
        </h1>
        <p className="text-body text-text-secondary mt-1">
          Here's your workspace summary.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="py-4">
                <div className="h-6 w-12 rounded bg-surface-secondary animate-pulse mb-2" />
                <div className="h-3 w-20 rounded bg-surface-secondary animate-pulse" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {statCards.map(({ label, sublabel, value, icon: Icon }) => (
            <Card key={label}>
              <CardContent className="flex flex-col gap-2 py-4 px-4">
                <div className="flex items-center justify-between">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <Icon size={18} />
                  </div>
                </div>
                <div>
                  <p className="text-2xl font-bold text-text-primary leading-none">{value}</p>
                  <p className="text-tiny text-text-secondary mt-1 uppercase tracking-wide">{label}</p>
                  <p className="text-tiny text-text-secondary">{sublabel}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Weekly activity</CardTitle>
        </CardHeader>
        <CardContent className="px-2">
          {loading ? (
            <div className="h-40 w-full rounded bg-surface-secondary animate-pulse" />
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart
                data={stats?.activity ?? []}
                margin={{ top: 4, right: 8, left: -28, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="analyses" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1A3C5E" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#1A3C5E" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="symptoms" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2E86AB" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2E86AB" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="combined" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: "11px" }} />
                <Area
                  type="monotone"
                  dataKey="analyses"
                  stroke="#1A3C5E"
                  fillOpacity={1}
                  fill="url(#analyses)"
                  name="X-Ray"
                />
                <Area
                  type="monotone"
                  dataKey="symptoms"
                  stroke="#2E86AB"
                  fillOpacity={1}
                  fill="url(#symptoms)"
                  name="Symptoms"
                />
                <Area
                  type="monotone"
                  dataKey="combined"
                  stroke="#8B5CF6"
                  fillOpacity={1}
                  fill="url(#combined)"
                  name="Combined"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}