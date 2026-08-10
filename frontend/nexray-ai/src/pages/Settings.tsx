// ============================================================
// NexRay AI - Settings Page
// Shows real doctor profile from JWT and system status.
// ============================================================

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getDoctor, logout } from "@/lib/api";
import { useNavigate } from "react-router-dom";
import { User, Hospital, Cpu, LogOut } from "lucide-react";

export default function Settings() {
  const doctor = getDoctor();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const systemServices = [
    { name: "X-Ray Analysis Engine", status: "Online" },
    { name: "Symptom Analysis Engine", status: "Online" },
    { name: "Report Generator", status: "Online" },
    { name: "Database", status: "Online" },
    { name: "Authentication", status: "Online" },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-page-title text-text-primary">Settings</h1>
        <p className="text-body text-text-secondary mt-1">
          Doctor profile and system status.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Doctor Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User size={18} />
              Doctor Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-label text-text-secondary">Full Name</label>
              <p className="text-body-sm font-medium text-text-primary">
                {doctor?.name ?? "—"}
              </p>
            </div>
            <div className="h-px bg-border" />
            <div className="flex flex-col gap-1.5">
              <label className="text-label text-text-secondary">Email</label>
              <p className="text-body-sm font-medium text-text-primary">
                {doctor?.email ?? "—"}
              </p>
            </div>
            <div className="h-px bg-border" />
            <div className="flex flex-col gap-1.5">
              <label className="text-label text-text-secondary">Role</label>
              <p className="text-body-sm font-medium text-text-primary">Medical Doctor</p>
            </div>
            <div className="h-px bg-border" />
            <Button
              variant="outline"
              className="w-full text-red-500 border-red-200 hover:bg-red-50 hover:text-red-600"
              onClick={handleLogout}
            >
              <LogOut size={15} className="mr-2" />
              Sign out
            </Button>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu size={18} />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {systemServices.map((s) => (
              <div key={s.name} className="flex items-center justify-between text-body-sm py-1">
                <span className="text-text-secondary">{s.name}</span>
                <span className="text-tiny font-medium px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                  ● {s.status}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* About */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hospital size={18} />
              About NexRay AI
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex flex-col gap-1">
                <p className="text-tiny text-text-secondary uppercase tracking-wide">Version</p>
                <p className="text-body-sm font-medium text-text-primary">1.0.0</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-tiny text-text-secondary uppercase tracking-wide">X-Ray Engine</p>
                <p className="text-body-sm font-medium text-text-primary">AI Vision</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-tiny text-text-secondary uppercase tracking-wide">Symptom Engine</p>
                <p className="text-body-sm font-medium text-text-primary">AI Language Model</p>
              </div>
              <div className="flex flex-col gap-1">
                <p className="text-tiny text-text-secondary uppercase tracking-wide">Built for</p>
                <p className="text-body-sm font-medium text-text-primary">Ghana & West Africa</p>
              </div>
            </div>
            <div className="h-px bg-border" />
            <p className="text-tiny text-text-secondary">
              NexRay AI is a clinical decision-support tool. All findings are AI-generated suggestions only.
              Clinical judgment of the attending medical professional must be applied before any action is taken.
            </p>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}